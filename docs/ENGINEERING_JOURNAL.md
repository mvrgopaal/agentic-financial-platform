2026-08-02

Today we introduced Provider Independence.

Initially the ProviderFactory owned the ConfigurationManager.

After discussion we realized the factory should only create providers.

This simplified the architecture and reduced coupling.

Lesson:
Factories should construct objects, not own application state.
