@echo off
set DJANGO_SETTINGS_MODULE=collaborative_editor.settings
daphne -b 0.0.0.0 -p 8000 collaborative_editor.asgi:application