// MD Reader - Tauri 2.0 Backend
// Provides all Tauri commands for the Markdown Reader application.

use serde::{Deserialize, Serialize};
use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::sync::Mutex;
use tauri::{AppHandle, Emitter, Manager};

/// Represents a file or directory entry in a directory listing.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FileEntry {
    /// Display name of the file or directory
    pub name: String,
    /// Full absolute path
    pub path: String,
    /// Whether this entry is a directory
    pub is_dir: bool,
}

/// Metadata about a file including size, modification time, and encoding.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FileMetadata {
    /// File size in bytes
    pub size: u64,
    /// Last modified timestamp as a human-readable string
    pub modified: String,
    /// Detected encoding (always "UTF-8" for text files)
    pub encoding: String,
}

/// Stored state for recent files list.
#[derive(Debug, Serialize, Deserialize, Default, Clone)]
struct RecentFiles {
    paths: Vec<String>,
}

/// Internal state for managing file watchers.
struct WatcherState {
    watchers: std::collections::HashMap<String, notify::RecommendedWatcher>,
}

impl WatcherState {
    fn new() -> Self {
        Self {
            watchers: std::collections::HashMap::new(),
        }
    }
}

/// Gets the path to the recent files JSON stored in the app data directory.
fn get_recent_files_path(app: &AppHandle) -> PathBuf {
    let data_dir = app
        .path()
        .app_data_dir()
        .expect("Failed to resolve app data directory");
    fs::create_dir_all(&data_dir).ok();
    data_dir.join("recent_files.json")
}

/// Reads the content of a file as a UTF-8 string.
///
/// Returns the file contents or an error if the file cannot be read
/// or is not valid UTF-8.
#[tauri::command]
fn read_file_content(path: String) -> Result<String, String> {
    fs::read_to_string(&path).map_err(|e| format!("Failed to read file '{}': {}", path, e))
}

/// Writes content to a file, creating it if it doesn't exist.
///
/// Overwrites existing file content. Returns an error if the write fails.
#[tauri::command]
fn write_file_content(path: String, content: String) -> Result<(), String> {
    let mut file = fs::File::create(&path)
        .map_err(|e| format!("Failed to create/open file '{}': {}", path, e))?;
    file.write_all(content.as_bytes())
        .map_err(|e| format!("Failed to write file '{}': {}", path, e))?;
    Ok(())
}

/// Lists the contents of a directory, sorted with directories first, then files.
///
/// Each entry contains the name, full path, and whether it is a directory.
/// Hidden files (starting with '.') are included.
#[tauri::command]
fn list_directory(path: String) -> Result<Vec<FileEntry>, String> {
    let dir_path = PathBuf::from(&path);

    if !dir_path.is_dir() {
        return Err(format!("'{}' is not a directory", path));
    }

    let entries: Vec<FileEntry> = fs::read_dir(&dir_path)
        .map_err(|e| format!("Failed to read directory '{}': {}", path, e))?
        .filter_map(|entry| {
            let entry = entry.ok()?;
            let file_name = entry.file_name().to_string_lossy().to_string();
            let full_path = entry.path().to_string_lossy().to_string();
            let is_dir = entry.path().is_dir();

            Some(FileEntry {
                name: file_name,
                path: full_path,
                is_dir,
            })
        })
        .collect();

    // Sort: directories first (alphabetically), then files (alphabetically)
    let mut sorted_entries = entries;
    sorted_entries.sort_by(|a, b| {
        match (a.is_dir, b.is_dir) {
            (true, false) => std::cmp::Ordering::Less,
            (false, true) => std::cmp::Ordering::Greater,
            _ => a.name.to_lowercase().cmp(&b.name.to_lowercase()),
        }
    });

    Ok(sorted_entries)
}

/// Reads the list of recently opened files from app data.
///
/// Returns a list of file paths, most recent first. Returns an empty
/// list if no recent files have been recorded yet.
#[tauri::command]
fn read_recent_files(app: AppHandle) -> Result<Vec<String>, String> {
    let recent_path = get_recent_files_path(&app);

    if !recent_path.exists() {
        return Ok(Vec::new());
    }

    let data = fs::read_to_string(&recent_path)
        .map_err(|e| format!("Failed to read recent files: {}", e))?;

    let recent: RecentFiles =
        serde_json::from_str(&data).map_err(|e| format!("Failed to parse recent files: {}", e))?;

    Ok(recent.paths)
}

/// Adds a file path to the recent files list.
///
/// The file is moved to the top of the list if it already exists (dedup).
/// The list is capped at 10 entries. The list is persisted to disk.
#[tauri::command]
fn add_recent_file(app: AppHandle, path: String) -> Result<(), String> {
    let recent_path = get_recent_files_path(&app);

    let mut recent: RecentFiles = if recent_path.exists() {
        let data = fs::read_to_string(&recent_path)
            .map_err(|e| format!("Failed to read recent files: {}", e))?;
        serde_json::from_str(&data).unwrap_or_default()
    } else {
        RecentFiles::default()
    };

    // Remove the path if it already exists (for dedup/move-to-top)
    recent.paths.retain(|p| p != &path);

    // Insert at the beginning (most recent first)
    recent.paths.insert(0, path);

    // Cap at 10 entries
    recent.paths.truncate(10);

    let json = serde_json::to_string_pretty(&recent)
        .map_err(|e| format!("Failed to serialize recent files: {}", e))?;

    fs::write(&recent_path, json)
        .map_err(|e| format!("Failed to save recent files: {}", e))?;

    Ok(())
}

/// Gets metadata about a file: size, last modified time, and encoding.
///
/// Encoding is detected as "UTF-8" for text-readable files.
#[tauri::command]
fn get_file_metadata(path: String) -> Result<FileMetadata, String> {
    let file_path = PathBuf::from(&path);

    if !file_path.exists() {
        return Err(format!("File '{}' does not exist", path));
    }

    let metadata = fs::metadata(&file_path)
        .map_err(|e| format!("Failed to read metadata for '{}': {}", path, e))?;

    let size = metadata.len();

    let modified = metadata
        .modified()
        .map(|t| {
            let datetime: chrono::DateTime<chrono::Local> = t.into();
            datetime.format("%Y-%m-%d %H:%M:%S").to_string()
        })
        .unwrap_or_else(|_| "Unknown".to_string());

    // Attempt to detect encoding by reading first few bytes
    let encoding = detect_encoding(&file_path);

    Ok(FileMetadata {
        size,
        modified,
        encoding,
    })
}

/// Simple encoding detection. Reads the file and checks if it's valid UTF-8.
fn detect_encoding(path: &PathBuf) -> String {
    match fs::read(path) {
        Ok(bytes) => {
            if std::str::from_utf8(&bytes).is_ok() {
                "UTF-8".to_string()
            } else {
                "Binary/Unknown".to_string()
            }
        }
        Err(_) => "Unknown".to_string(),
    }
}

/// Starts watching a file for changes and emits a `file-changed` event
/// to the frontend whenever the file is modified, created, or deleted.
///
/// Uses the `notify` crate with debouncing to avoid rapid-fire events.
/// Only one watcher per file path is active at a time.
#[tauri::command]
fn watch_file_changes(app: AppHandle, path: String) -> Result<(), String> {
    let state = app.state::<Mutex<WatcherState>>();
    let mut state = state.lock().map_err(|e| format!("Lock error: {}", e))?;

    // If already watching this path, skip
    if state.watchers.contains_key(&path) {
        return Ok(());
    }

    use notify::{Event, RecursiveMode, Watcher};
    use std::sync::mpsc;

    let (tx, rx) = mpsc::channel::<notify::Result<Event>>();
    let watch_path = path.clone();
    let app_handle = app.clone();

    // Create a watcher with a debounce configuration
    let mut watcher = notify::recommended_watcher(move |res: notify::Result<Event>| {
        let _ = tx.send(res);
    })
    .map_err(|e| format!("Failed to create file watcher: {}", e))?;

    // Watch the file
    watcher
        .watch(std::path::Path::new(&path), RecursiveMode::NonRecursive)
        .map_err(|e| format!("Failed to watch file '{}': {}", path, e))?;

    // Spawn a thread to handle watcher events and emit to frontend
    let emit_path = watch_path.clone();
    std::thread::spawn(move || {
        // Simple debounce: wait briefly after receiving an event before emitting
        let mut last_event_time = std::time::Instant::now();
        let debounce_duration = std::time::Duration::from_millis(300);
        let mut pending = false;

        loop {
            match rx.recv_timeout(std::time::Duration::from_millis(100)) {
                Ok(Ok(_event)) => {
                    last_event_time = std::time::Instant::now();
                    pending = true;
                }
                Ok(Err(e)) => {
                    eprintln!("Watch error for '{}': {:?}", emit_path, e);
                }
                Err(mpsc::RecvTimeoutError::Timeout) => {
                    if pending && last_event_time.elapsed() >= debounce_duration {
                        // Emit the file-changed event to the frontend
                        let _ = app_handle.emit(
                            "file-changed",
                            serde_json::json!({
                                "path": emit_path,
                                "timestamp": chrono::Utc::now().to_rfc3339(),
                            }),
                        );
                        pending = false;
                    }
                }
                Err(mpsc::RecvTimeoutError::Disconnected) => {
                    // Watcher was dropped, exit the thread
                    break;
                }
            }
        }
    });

    // Store the watcher so it stays alive
    state.watchers.insert(watch_path, watcher);

    Ok(())
}

/// Stops watching a file for changes.
///
/// Removes the watcher for the given path. No further `file-changed`
/// events will be emitted for this file.
#[tauri::command]
fn unwatch_file(app: AppHandle, path: String) -> Result<(), String> {
    let state = app.state::<Mutex<WatcherState>>();
    let mut state = state.lock().map_err(|e| format!("Lock error: {}", e))?;

    if let Some(mut watcher) = state.watchers.remove(&path) {
        use notify::Watcher;
        watcher
            .unwatch(std::path::Path::new(&path))
            .map_err(|e| format!("Failed to unwatch file '{}': {}", path, e))?;
    }

    Ok(())
}

/// Initializes and runs the Tauri application.
///
/// Sets up all plugins (dialog, fs) and registers all commands.
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .manage(Mutex::new(WatcherState::new()))
        .invoke_handler(tauri::generate_handler![
            read_file_content,
            write_file_content,
            list_directory,
            read_recent_files,
            add_recent_file,
            get_file_metadata,
            watch_file_changes,
            unwatch_file,
        ])
        .run(tauri::generate_context!())
        .expect("Error while running MD Reader application");
}
