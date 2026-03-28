#!/usr/bin/env python

import json
import subprocess
from pathlib import Path
import argparse
import re

BASE_DIR = Path(__file__).resolve().parent
THEMES_FILE = BASE_DIR / "themes.json"

def load_themes():
  with open(THEMES_FILE, "r") as f:
    return json.load(f)
def update_conky(theme):
  conky = theme.get("conky", None)
  if conky is None:
    return

  configs = {
    "regulus": Path.home() / ".config/conky/Regulus/Regulus.conf",
    "mirach": Path.home() / ".config/conky/Mirach/Mirach.conf"
  }

  for name, cfg in configs.items():
    if not cfg.exists():
      continue

    if name not in conky:
      continue

    content = cfg.read_text()
    conf_data = conky[name]


    if "alignment" in conf_data:
      content = re.sub(r"alignment\s*=\s*'[^']+'", f"alignment = '{conf_data['alignment']}'", content)

    if "avatar" in conf_data:
      content = re.sub(r"~/.config/conky/Regulus/res/avatar/[^ ]+\.png", conf_data["avatar"], content)

    for key, value in conf_data.get("fonts", {}).items():
      content = re.sub(rf"{key}\s*=\s*'[^']+'", f"{key} = '{value}'", content)

    for key, value in conf_data.get("colors", {}).items():
      content = re.sub(rf"{key}\s*=\s*'[^']+'", f"{key} = '{value}'", content)

    cfg.write_text(content)
    print(f"🎛 Updated {name} conky config")

  subprocess.run(["pkill", "conky"])
  for cfg in configs.values():
    if cfg.exists():
      subprocess.Popen(["conky", "-c", str(cfg)])

def apply_neofetch(name: str):
  neofetch_source = Path.home() / ".config/fish/conf.d/neofetch.fish"
  if neofetch_source.exists():
    content = neofetch_source.read_text()
    content = re.sub(r'set FILENAME "[^"]+"', f'set FILENAME "{name}"', content)
    neofetch_source.write_text(content)
    print(f"Updated neofetch config to use {name}")

def apply_theme(name: str):
  themes = load_themes()
  if name not in themes:
    print(f"Theme {name} not found")
    return

  theme = themes[name]

  if "wallpaper" in theme:
    subprocess.run([
      "gsettings",
      "set",
      "org.gnome.desktop.background",
      "picture-uri",
      f"file://{theme['wallpaper']}"
    ])
    subprocess.run([
      "gsettings",
      "set",
      "org.gnome.desktop.background",
      "picture-uri-dark",
      f"file://{theme['wallpaper']}"
    ])
    print(f"Set wallpaper to {theme['wallpaper']}")

  if "icons" in theme:
    subprocess.run([
      "gsettings",
      "set",
      "org.gnome.desktop.interface",
      "icon-theme",
      theme["icons"]
    ])
    print(f"Set icon theme to {theme['icons']}")

  #if "font" in theme:
  #  subprocess.run([
  #    "gsettings",
  #    "set",
  #    "org.gnome.desktop.interface",
  #    "font-family",
  #    theme["font"]
  #  ])
  #  print(f"Set font to {theme['font']}")

  if "cursor" in theme:
    subprocess.run([
      "gsettings",
      "set",
      "org.gnome.desktop.interface",
      "cursor-theme",
      theme["cursor"]
    ])
    print(f"Set cursor theme to {theme['cursor']}")

  #if "gtk" in theme:
  #  subprocess.run([
  #    "gsettings",
  #    "set",
  #    "org.gnome.desktop.interface",
  #    "gtk-theme",
  #    theme["gtk"]
  #  ])
  #  print(f"Set gtk theme to {theme['gtk']}")

  #if "shell" in theme:
  #  subprocess.run([
  #    "gsettings",
  #    "set",
  #    "org.gnome.shell.extensions.user-theme",
  #    "name",
  #    theme["shell"]
  #  ])
  #  print(f"Set shell theme to {theme['shell']}")

  if "conky" in theme:
    update_conky(theme)
    print(f"Updated conky theme {name}")

  if "neofetch" in theme:
    apply_neofetch(theme["neofetch"])
    print(f"Updated neofetch theme {name}")

  print(f"Applied theme {name}")

def list_themes():
  themes = load_themes()
  for name in themes:
    print(f"- {name}")

def main():
  parser = argparse.ArgumentParser(description="Switch between Gnome themes")
  subparsers = parser.add_subparsers(dest="command")

  subparsers.add_parser("list", help="List available themes")
  apply_parser = subparsers.add_parser("apply", help="Apply a theme")
  apply_parser.add_argument("theme", help="Name of the theme to apply")

  args = parser.parse_args()

  if args.command == "list":
    list_themes()
  elif args.command == "apply":
    if not args.theme:
      print("Please specify a theme to apply")
      list_themes()
      return
    apply_theme(args.theme)
  else:
    parser.print_help()

if __name__ == "__main__":
  main()
