#!/usr/bin/env bash

set -ex

ABLETON_PATH="$(cat ableton-path)"
REMOTE_SCRIPTS_PATH="$ABLETON_PATH/Contents/App-Resources/MIDI Remote Scripts/"

tar -czvf backup.tar.gz "$REMOTE_SCRIPTS_PATH"

