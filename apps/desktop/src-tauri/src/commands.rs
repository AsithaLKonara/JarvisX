/**
 * Tauri Commands - Native system control from JavaScript
 */

use tauri::Window;

#[tauri::command]
pub async fn open_application(app_name: String) -> Result<String, String> {
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let output = Command::new("open")
            .arg("-a")
            .arg(&app_name)
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Opened: {}", app_name))
        } else {
            Err(format!("❌ Failed to open: {}", app_name))
        }
    }

    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        let output = Command::new("cmd")
            .args(&["/C", "start", "", &app_name])
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Opened: {}", app_name))
        } else {
            Err(format!("❌ Failed to open: {}", app_name))
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        let output = Command::new("xdg-open")
            .arg(&app_name)
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Opened: {}", app_name))
        } else {
            Err(format!("❌ Failed to open: {}", app_name))
        }
    }
}

#[tauri::command]
pub async fn execute_command(command: String, args: Vec<String>) -> Result<String, String> {
    use std::process::Command;

    // Whitelist of allowed commands for security
    let allowed_commands = vec!["git", "npm", "ls", "pwd", "echo"];
    
    if !allowed_commands.contains(&command.as_str()) {
        return Err(format!("❌ Command not whitelisted: {}", command));
    }

    let output = Command::new(&command)
        .args(&args)
        .output()
        .map_err(|e| e.to_string())?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    if output.status.success() {
        Ok(stdout)
    } else {
        Err(stderr)
    }
}

#[tauri::command]
pub async fn get_system_info() -> Result<serde_json::Value, String> {
    use sysinfo::{System, SystemExt};
    
    let mut sys = System::new_all();
    sys.refresh_all();

    let info = serde_json::json!({
        "os": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "hostname": sys.host_name(),
        "cpuCount": sys.cpus().len(),
        "totalMemory": sys.total_memory(),
        "usedMemory": sys.used_memory(),
        "uptime": sys.uptime(),
    });

    Ok(info)
}

#[tauri::command]
pub async fn simulate_keyboard(key: String) -> Result<String, String> {
    use enigo::{Enigo, Mouse, Keyboard, Direction, Settings, Key};
    
    let mut enigo = Enigo::new(&Settings::default(), Mouse, Keyboard).map_err(|e| e.to_string())?;
    
    // Parse key and simulate press
    let key_enum = match key.to_lowercase().as_str() {
        "enter" | "return" => Key::Return,
        "space" => Key::Space,
        "tab" => Key::Tab,
        "escape" | "esc" => Key::Escape,
        "backspace" => Key::Backspace,
        "delete" | "del" => Key::Delete,
        "up" => Key::UpArrow,
        "down" => Key::DownArrow,
        "left" => Key::LeftArrow,
        "right" => Key::RightArrow,
        "home" => Key::Home,
        "end" => Key::End,
        "pageup" | "pgup" => Key::PageUp,
        "pagedown" | "pgdown" => Key::PageDown,
        "f1" => Key::F1,
        "f2" => Key::F2,
        "f3" => Key::F3,
        "f4" => Key::F4,
        "f5" => Key::F5,
        "f6" => Key::F6,
        "f7" => Key::F7,
        "f8" => Key::F8,
        "f9" => Key::F9,
        "f10" => Key::F10,
        "f11" => Key::F11,
        "f12" => Key::F12,
        "ctrl" => Key::Control,
        "alt" => Key::Alt,
        "shift" => Key::Shift,
        "cmd" | "command" | "meta" => Key::Meta,
        _ => {
            // For single characters, try to parse as Key::Unicode
            if key.len() == 1 {
                Key::Unicode(key.chars().next().unwrap())
            } else {
                return Err(format!("Unsupported key: {}", key));
            }
        }
    };
    
    enigo.key(key_enum, Direction::Press).map_err(|e| e.to_string())?;
    enigo.key(key_enum, Direction::Release).map_err(|e| e.to_string())?;
    
    println!("🎹 Simulating keyboard: {}", key);
    Ok(format!("Pressed: {}", key))
}

#[tauri::command]
pub async fn simulate_mouse_click(x: i32, y: i32) -> Result<String, String> {
    use enigo::{Enigo, Mouse, Keyboard, Direction, Settings};
    
    let mut enigo = Enigo::new(&Settings::default(), Mouse, Keyboard).map_err(|e| e.to_string())?;
    
    // Move to position and click
    enigo.move_mouse(x, y, Direction::Absolute).map_err(|e| e.to_string())?;
    enigo.button(Mouse::Left, Direction::Press).map_err(|e| e.to_string())?;
    enigo.button(Mouse::Left, Direction::Release).map_err(|e| e.to_string())?;
    
    println!("🖱️  Mouse click at: ({}, {})", x, y);
    Ok(format!("Clicked at: ({}, {})", x, y))
}

#[tauri::command]
pub async fn simulate_mouse_drag(x1: i32, y1: i32, x2: i32, y2: i32) -> Result<String, String> {
    use enigo::{Enigo, Mouse, Keyboard, Direction, Settings};
    
    let mut enigo = Enigo::new(&Settings::default(), Mouse, Keyboard).map_err(|e| e.to_string())?;
    
    // Move to start position, press mouse, drag to end position, release
    enigo.move_mouse(x1, y1, Direction::Absolute).map_err(|e| e.to_string())?;
    enigo.button(Mouse::Left, Direction::Press).map_err(|e| e.to_string())?;
    
    // Smooth drag by moving in steps
    let steps = 10;
    let dx = (x2 - x1) as f32 / steps as f32;
    let dy = (y2 - y1) as f32 / steps as f32;
    
    for i in 1..=steps {
        let x = x1 + (dx * i as f32) as i32;
        let y = y1 + (dy * i as f32) as i32;
        enigo.move_mouse(x, y, Direction::Absolute).map_err(|e| e.to_string())?;
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
    
    enigo.button(Mouse::Left, Direction::Release).map_err(|e| e.to_string())?;
    
    println!("🖱️  Mouse drag from: ({}, {}) to ({}, {})", x1, y1, x2, y2);
    Ok(format!("Dragged from ({}, {}) to ({}, {})", x1, y1, x2, y2))
}

#[tauri::command]
pub async fn simulate_mouse_scroll(direction: String, amount: i32) -> Result<String, String> {
    use enigo::{Enigo, Mouse, Keyboard, Direction, Settings};
    
    let mut enigo = Enigo::new(&Settings::default(), Mouse, Keyboard).map_err(|e| e.to_string())?;
    
    // Scroll based on direction
    let scroll_amount = match direction.to_lowercase().as_str() {
        "up" | "north" => -amount,
        "down" | "south" => amount,
        "left" | "west" => -amount,
        "right" | "east" => amount,
        _ => amount, // Default to down
    };
    
    enigo.scroll(scroll_amount, Direction::Absolute).map_err(|e| e.to_string())?;
    
    println!("🖱️  Mouse scroll: {} by {}", direction, amount);
    Ok(format!("Scrolled {} by {}", direction, amount))
}

#[tauri::command]
pub async fn get_mouse_position() -> Result<serde_json::Value, String> {
    use enigo::{Enigo, Mouse, Keyboard, Direction, Settings};
    
    let mut enigo = Enigo::new(&Settings::default(), Mouse, Keyboard).map_err(|e| e.to_string())?;
    
    // Get current mouse position
    let (x, y) = enigo.location().map_err(|e| e.to_string())?;
    
    let position = serde_json::json!({
        "x": x,
        "y": y
    });
    Ok(position)
}

#[tauri::command]
pub async fn simulate_mouse_hover(x: i32, y: i32) -> Result<String, String> {
    use enigo::{Enigo, Mouse, Keyboard, Direction, Settings};
    
    let mut enigo = Enigo::new(&Settings::default(), Mouse, Keyboard).map_err(|e| e.to_string())?;
    
    // Move mouse to position without clicking
    enigo.move_mouse(x, y, Direction::Absolute).map_err(|e| e.to_string())?;
    
    // Wait a bit to simulate hover
    std::thread::sleep(std::time::Duration::from_millis(100));
    
    println!("🖱️  Mouse hover at: ({}, {})", x, y);
    Ok(format!("Hovered at: ({}, {})", x, y))
}

#[tauri::command]
pub async fn get_running_processes() -> Result<Vec<String>, String> {
    use sysinfo::{ProcessExt, System, SystemExt};
    
    let mut sys = System::new_all();
    sys.refresh_all();

    let processes: Vec<String> = sys
        .processes()
        .iter()
        .map(|(pid, process)| format!("{}: {}", pid, process.name()))
        .collect();

    Ok(processes)
}

#[tauri::command]
pub async fn switch_to_application(app_name: String) -> Result<String, String> {
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let output = Command::new("osascript")
            .arg("-e")
            .arg(format!("tell application \"{}\" to activate", app_name))
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Switched to: {}", app_name))
        } else {
            Err(format!("❌ Failed to switch to: {}", app_name))
        }
    }

    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        let output = Command::new("powershell")
            .args(&["-Command", &format!("Get-Process {} | ForEach-Object {{ $_.MainWindowTitle }}", app_name)])
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Switched to: {}", app_name))
        } else {
            Err(format!("❌ Failed to switch to: {}", app_name))
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        let output = Command::new("wmctrl")
            .arg("-a")
            .arg(&app_name)
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Switched to: {}", app_name))
        } else {
            Err(format!("❌ Failed to switch to: {}", app_name))
        }
    }
}

#[tauri::command]
pub async fn minimize_application(app_name: String) -> Result<String, String> {
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let output = Command::new("osascript")
            .arg("-e")
            .arg(format!("tell application \"{}\" to set minimized of window 1 to true", app_name))
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Minimized: {}", app_name))
        } else {
            Err(format!("❌ Failed to minimize: {}", app_name))
        }
    }

    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        let output = Command::new("powershell")
            .args(&["-Command", &format!("Get-Process {} | ForEach-Object {{ $_.MinimizeMainWindow() }}", app_name)])
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Minimized: {}", app_name))
        } else {
            Err(format!("❌ Failed to minimize: {}", app_name))
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        let output = Command::new("wmctrl")
            .arg("-r")
            .arg(&app_name)
            .arg("-b")
            .arg("add,hidden")
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Minimized: {}", app_name))
        } else {
            Err(format!("❌ Failed to minimize: {}", app_name))
        }
    }
}

#[tauri::command]
pub async fn maximize_application(app_name: String) -> Result<String, String> {
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let output = Command::new("osascript")
            .arg("-e")
            .arg(format!("tell application \"{}\" to set zoomed of window 1 to true", app_name))
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Maximized: {}", app_name))
        } else {
            Err(format!("❌ Failed to maximize: {}", app_name))
        }
    }

    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        let output = Command::new("powershell")
            .args(&["-Command", &format!("Get-Process {} | ForEach-Object {{ $_.MaximizeMainWindow() }}", app_name)])
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Maximized: {}", app_name))
        } else {
            Err(format!("❌ Failed to maximize: {}", app_name))
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        let output = Command::new("wmctrl")
            .arg("-r")
            .arg(&app_name)
            .arg("-b")
            .arg("add,maximized_vert,maximized_horz")
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Maximized: {}", app_name))
        } else {
            Err(format!("❌ Failed to maximize: {}", app_name))
        }
    }
}

#[tauri::command]
pub async fn close_application(app_name: String) -> Result<String, String> {
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let output = Command::new("osascript")
            .arg("-e")
            .arg(format!("tell application \"{}\" to quit", app_name))
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Closed: {}", app_name))
        } else {
            Err(format!("❌ Failed to close: {}", app_name))
        }
    }

    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        let output = Command::new("taskkill")
            .arg("/F")
            .arg("/IM")
            .arg(&format!("{}.exe", app_name))
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Closed: {}", app_name))
        } else {
            Err(format!("❌ Failed to close: {}", app_name))
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        let output = Command::new("pkill")
            .arg(&app_name)
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Closed: {}", app_name))
        } else {
            Err(format!("❌ Failed to close: {}", app_name))
        }
    }
}

#[tauri::command]
pub async fn get_window_list() -> Result<Vec<serde_json::Value>, String> {
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let output = Command::new("osascript")
            .arg("-e")
            .arg("tell application \"System Events\" to get name of every process whose background only is false")
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            let windows: Vec<serde_json::Value> = String::from_utf8_lossy(&output.stdout)
                .split(", ")
                .map(|name| serde_json::json!({
                    "name": name.trim(),
                    "title": name.trim()
                }))
                .collect();
            Ok(windows)
        } else {
            Err("Failed to get window list".to_string())
        }
    }

    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        let output = Command::new("powershell")
            .args(&["-Command", "Get-Process | Where-Object {$_.MainWindowTitle -ne \"\"} | Select-Object Name, MainWindowTitle | ConvertTo-Json"])
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            let json_str = String::from_utf8_lossy(&output.stdout);
            let windows: Vec<serde_json::Value> = serde_json::from_str(&json_str).unwrap_or_default();
            Ok(windows)
        } else {
            Err("Failed to get window list".to_string())
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        let output = Command::new("wmctrl")
            .arg("-l")
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            let windows: Vec<serde_json::Value> = String::from_utf8_lossy(&output.stdout)
                .lines()
                .map(|line| {
                    let parts: Vec<&str> = line.splitn(4, ' ').collect();
                    if parts.len() >= 4 {
                        serde_json::json!({
                            "id": parts[0],
                            "desktop": parts[1],
                            "title": parts[3]
                        })
                    } else {
                        serde_json::json!({})
                    }
                })
                .collect();
            Ok(windows)
        } else {
            Err("Failed to get window list".to_string())
        }
    }
}

#[tauri::command]
pub async fn focus_window(title: String) -> Result<String, String> {
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let output = Command::new("osascript")
            .arg("-e")
            .arg(format!("tell application \"System Events\" to set frontmost of first process whose name contains \"{}\" to true", title))
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Focused window: {}", title))
        } else {
            Err(format!("❌ Failed to focus window: {}", title))
        }
    }

    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        let output = Command::new("powershell")
            .args(&["-Command", &format!("Get-Process | Where-Object {{$_.MainWindowTitle -like \"*{}*\"}} | ForEach-Object {{ $_.SetForegroundWindow() }}", title)])
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Focused window: {}", title))
        } else {
            Err(format!("❌ Failed to focus window: {}", title))
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        let output = Command::new("wmctrl")
            .arg("-a")
            .arg(&title)
            .output()
            .map_err(|e| e.to_string())?;

        if output.status.success() {
            Ok(format!("✅ Focused window: {}", title))
        } else {
            Err(format!("❌ Failed to focus window: {}", title))
        }
    }
}

#[tauri::command]
pub async fn set_window_always_on_top(window: Window, always_on_top: bool) -> Result<(), String> {
    window
        .set_always_on_top(always_on_top)
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub async fn hide_window(window: Window) -> Result<(), String> {
    window.hide().map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub async fn show_window(window: Window) -> Result<(), String> {
    window.show().map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub async fn set_avatar_emotion(emotion: String) -> Result<String, String> {
    println!("🎭 Setting avatar emotion: {}", emotion);
    // This will send request to avatar service
    Ok(format!("Emotion set to: {}", emotion))
}

#[tauri::command]
pub async fn get_avatar_state() -> Result<serde_json::Value, String> {
    // Fetch from avatar service
    let state = serde_json::json!({
        "emotion": "optimistic",
        "intensity": 0.7,
        "isListening": false,
        "isSpeaking": false
    });
    Ok(state)
}

#[tauri::command]
pub async fn capture_screen() -> Result<String, String> {
    use screenshots::Screen;
    use std::io::Cursor;
    use base64::{Engine as _, engine::general_purpose};
    
    // Get all screens
    let screens = Screen::all().map_err(|e| e.to_string())?;
    
    if screens.is_empty() {
        return Err("No screens found".to_string());
    }
    
    // Capture the first screen
    let screen = &screens[0];
    let image = screen.capture().map_err(|e| e.to_string())?;
    
    // Convert to base64
    let mut cursor = Cursor::new(Vec::new());
    image.write_to(&mut cursor, image::ImageOutputFormat::Png).map_err(|e| e.to_string())?;
    let image_data = cursor.into_inner();
    let base64_image = general_purpose::STANDARD.encode(&image_data);
    
    Ok(base64_image)
}

#[tauri::command]
pub async fn get_system_uptime() -> Result<String, String> {
    use sysinfo::{System, SystemExt};
    
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let uptime = sys.uptime();
    let hours = uptime / 3600;
    let minutes = (uptime % 3600) / 60;
    
    Ok(format!("{}h {}m", hours, minutes))
}

#[tauri::command]
pub async fn capture_screen_region(x: i32, y: i32, width: i32, height: i32) -> Result<String, String> {
    use screenshots::Screen;
    use std::io::Cursor;
    use base64::{Engine as _, engine::general_purpose};
    
    // Get all screens
    let screens = Screen::all().map_err(|e| e.to_string())?;
    
    if screens.is_empty() {
        return Err("No screens found".to_string());
    }
    
    // Capture the first screen
    let screen = &screens[0];
    let image = screen.capture_area(x, y, width as u32, height as u32).map_err(|e| e.to_string())?;
    
    // Convert to base64
    let mut cursor = Cursor::new(Vec::new());
    image.write_to(&mut cursor, image::ImageOutputFormat::Png).map_err(|e| e.to_string())?;
    let image_data = cursor.into_inner();
    let base64_image = general_purpose::STANDARD.encode(&image_data);
    
    Ok(base64_image)
}

#[tauri::command]
pub async fn get_system_uptime() -> Result<String, String> {
    use sysinfo::{System, SystemExt};
    
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let uptime = sys.uptime();
    let hours = uptime / 3600;
    let minutes = (uptime % 3600) / 60;
    
    Ok(format!("{}h {}m", hours, minutes))
}

