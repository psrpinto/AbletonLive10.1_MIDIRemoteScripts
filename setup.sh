#!/usr/bin/env bash

set -ex

CUSTOM_SCRIPTS_PATH=$PWD
APP_RESOURCES_PATH="$(cat ableton-path)/Contents/App-Resources"

rm -rf "$APP_RESOURCES_PATH/MIDI Remote Scripts/"

cd "$APP_RESOURCES_PATH"
ln -s "$CUSTOM_SCRIPTS_PATH" "MIDI Remote Scripts"
