import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

global_phrase = ''


def run_int(event, phrase_lock):
    """Interpreter thread worker function"""
    logging.debug('Starting Imports')
    import Interpreter as Int
    global global_phrase
    logging.debug('Finished Imports')
    local_phrase = ''
    while True:
        while not event.isSet():
            event.wait(2)
        with phrase_lock:
            logging.debug('Event set')
            local_phrase = global_phrase
            event.clear()
        Int.parse_phrase(local_phrase)


def run_spt(event, phrase_lock):
    """SpeechToTex thread worker function"""
    logging.debug('Starting Imports')
    import SpeechToText as Spt
    global global_phrase
    logging.debug('Finished Imports')
    sd = Spt.SpeechDetector()
    sd.setup_mic()
    local_phrase = ''
    while True:
        local_phrase = sd.run()
        if event.isSet():
            logging.debug('Event already set')
        else:
            with phrase_lock:
                logging.debug('Setting event')
                event.set()
                global_phrase = local_phrase


if __name__ == '__main__':
    threads = []

    lock = threading.Lock()

    phrase_detected_event = threading.Event()

    int_thread = threading.Thread(name='interpreter_thread', target=run_int, args = (phrase_detected_event, lock, ))
    spt_thread = threading.Thread(name='speech_thread', target=run_spt, args = (phrase_detected_event, lock, ))

    threads.append(int_thread)
    threads.append(spt_thread)

    for t in threads:
        t.start()
