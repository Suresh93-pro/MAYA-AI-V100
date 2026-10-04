# MAYA AI Architecture

MAYA follows a modular architecture:

User
  |
  +-- Voice Listener
  |
  +-- Text Input
          |
          v
    Command Engine
       /       \
      /         \
Launcher       AI Brain
   |              |
Windows        Local AI
   |
Speaker / Response

The desktop interface is implemented with Tkinter.
