# This will add the necessary jobs to the queue to update the timetables

from rq import Queue
from worker import conn
from update import update_all
q = Queue(connection=conn)

# This will add to the queue
q.enqueue(update_all)
