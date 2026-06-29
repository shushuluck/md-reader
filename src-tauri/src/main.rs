// MD Reader - Tauri 2.0 Application
// Main entry point that initializes the Tauri application with plugins and commands.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    md_reader_lib::run()
}
