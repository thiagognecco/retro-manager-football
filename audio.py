"""Audio layer with optional game sounds and headless (no-audio) fallback.

Attempts to use pygame.mixer when available. If pygame or audio hardware is unavailable,
functions become no-ops so the game can run in headless environments (CI, servers).

API:
- set_audio_enabled(enabled: bool)
- set_sounds_enabled(enabled: bool)
- play_sound(path_or_key: str)

The implementation is intentionally small and defensive: failures to initialize or
play audio are caught and treated as no-ops.
"""
from typing import Optional
import os

_audio_enabled = True
_sounds_enabled = True

# Internal mixer handle (if initialized)
_mixer = None


def _try_init_pygame_mixer() -> Optional[object]:
    """Try to import and initialize pygame.mixer. Return the mixer module or None on failure."""
    try:
        # Import lazily to avoid hard dependency
        import pygame
        # If SDL audio driver environment variable is not set, allow SDL to decide.
        # In headless environments, pygame.mixer.init() may still succeed or raise; catch exceptions.
        try:
            pygame.mixer.init()
        except Exception:
            # Attempt to set a dummy audio driver and retry (helps on some CI/headless setups)
            try:
                os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
                pygame.mixer.quit()
                pygame.mixer.init()
            except Exception:
                return None
        return pygame.mixer
    except Exception:
        return None


# Initialize mixer at import-time (best-effort). If this fails, _mixer stays None and playback is no-op.
_mixer = _try_init_pygame_mixer()


def set_audio_enabled(enabled: bool) -> None:
    global _audio_enabled
    _audio_enabled = bool(enabled)


def set_sounds_enabled(enabled: bool) -> None:
    global _sounds_enabled
    _sounds_enabled = bool(enabled)


def is_audio_available() -> bool:
    """Return True if an audio backend is available and initialized."""
    return _mixer is not None


def play_sound(path_or_key: Optional[str]) -> None:
    """Play a sound identified by a path or key.

    This is intentionally forgiving: any error or missing backend becomes a no-op.
    """
    if not _audio_enabled or not _sounds_enabled:
        return
    if not path_or_key:
        return

    if _mixer is None:
        # No mixer available — headless / fallback behavior: no-op
        return

    try:
        # If caller provided a path to a file that exists, load it; otherwise attempt to treat the
        # argument as a resource key and let pygame raise if it's invalid.
        if os.path.isfile(path_or_key):
            sound = _mixer.Sound(path_or_key)
        else:
            # Let pygame resolve non-file resources; this may raise — catch below.
            sound = _mixer.Sound(path_or_key)
        sound.play()
    except Exception:
        # Any failure should not crash the game — swallow exceptions and no-op
        return


# Convenience alias
play = play_sound
