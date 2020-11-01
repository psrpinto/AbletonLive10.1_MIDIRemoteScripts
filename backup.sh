#!/usr/bin/env bash

set -ex

APP_RESOURCES_PATH="$(cat ableton-path)/Contents/App-Resources"

tar czvf backup.tar.gz -C "$APP_RESOURCES_PATH" "$APP_RESOURCES_PATH/MIDI Remote Scripts"

