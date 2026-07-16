import audio


def test_audio_headless_no_exceptions():
    # Ensure toggles can be set and calling play_sound in environments without audio
    # backend does not raise exceptions.
    audio.set_audio_enabled(True)
    audio.set_sounds_enabled(True)
    # Should not raise even if file doesn't exist or mixer is unavailable
    audio.play_sound("nonexistent_sound_file_for_test.wav")

    # Disable sounds - should be a no-op
    audio.set_sounds_enabled(False)
    audio.play_sound("nonexistent_sound_file_for_test.wav")

    # Disable audio entirely - should be a no-op
    audio.set_audio_enabled(False)
    audio.play_sound("nonexistent_sound_file_for_test.wav")

    # Check is_audio_available() doesn't raise
    _ = audio.is_audio_available()

    assert True
