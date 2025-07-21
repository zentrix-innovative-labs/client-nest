from .tasks import process_event

# Example stub for queue consumer

def handle_incoming_event(event_data):
    # This function would be called by your queue listener
    process_event.delay(event_data) 