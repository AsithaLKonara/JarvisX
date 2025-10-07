// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod voice;
mod system;
mod screen;

use commands::*;
use voice::*;
use system::*;
use screen::*;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            // System control
            open_application,
            execute_command,
            get_system_info,
            simulate_keyboard,
            simulate_mouse_click,
            simulate_mouse_drag,
            simulate_mouse_scroll,
            get_mouse_position,
            simulate_mouse_hover,
            get_running_processes,
            // App management
            switch_to_application,
            minimize_application,
            maximize_application,
            close_application,
            get_window_list,
            focus_window,
            // Voice
            start_microphone,
            stop_microphone,
            get_audio_devices,
            process_audio_chunk,
            // Screen
            capture_screen,
            capture_screen_region,
            start_screen_stream,
            stop_screen_stream,
            // System
            get_system_uptime,
            // Avatar
            set_avatar_emotion,
            get_avatar_state,
            // Window management
            set_window_always_on_top,
            hide_window,
            show_window,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

