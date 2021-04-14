class EventDispatcher:
    """Mixin class for dispatching events when state changes."""

    def __init__(self, event_listener=None):
        """Initialize an EventDispatcher with an optional event listener."""
        self.event_listener = event_listener

    def on_state_changed(self, state):
        """To invoke any event listeners, subclasses should call this method with their new state."""
        if self.event_listener is not None:
            try:
                self.event_listener(state)
            except Exception as e:
                print(f'Caught exception while running event listener: {e}')
