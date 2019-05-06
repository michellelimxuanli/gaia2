from unit.unit import TestCalculator
from src.pendingwork import PendingWork
from src.util import EmptyQueueError
from src.ml_thread import initialize_current_node   

def test_pending_work(calc):
    calc.context("test_pending_work")
    pending_work_queues = PendingWork(100)

    # Testing if setup successfully creates queues
    pending_work_queues.setup(
        "localhost:5000", ["localhost:5001", "localhost:5002"]) 
    node = initialize_current_node(pending_work_queues, 'MNIST', './data')
    pending_work_queues.setup_connection_to_node(node)   
    check = pending_work_queues.get_total_no_of_updates() == 0
    if not check:
        print("queues created", pending_work_queues)
        calc.check(False)
        return

    # Testing if enqueue adds items to correct queues
    pending_work_queues.enqueue("5001 update", "localhost:5001")
    calc.check(pending_work_queues.get_total_no_of_updates() == 1)
    pending_work_queues.enqueue("5001 update 2", "localhost:5001")
    calc.check(pending_work_queues.get_total_no_of_updates() == 2)
    pending_work_queues.enqueue("5000 update", "localhost:5000")
    check = pending_work_queues.get_total_no_of_updates() == 3
    if not check:
        calc.check(False)
        print("queues after 3 things are added", pending_work_queues)
        return

    # Testing if dequeue works
    pending_work_queues.dequeue_random()
    check = pending_work_queues.get_total_no_of_updates() == 2
    if not check:
        calc.check(False)
        print("queues after 1 item removed", pending_work_queues)
        return
    pending_work_queues.dequeue_random()
    check = pending_work_queues.get_total_no_of_updates() == 1
    if not check:
        calc.check(False)
        print("queues after 1 item removed", pending_work_queues)
        return
    pending_work_queues.dequeue_random()
    check = pending_work_queues.get_total_no_of_updates() == 0
    if not check:
        calc.check(False)
        print("queues after another 2 items removed",
            pending_work_queues)
        return

    # Testing if dequeue works when queue empty
    try:
        item = pending_work_queues.dequeue_random()
        calc.check(False)
    except EmptyQueueError:
        calc.check(True)

    # Testing if dequeue everything works 
    pending_work_queues.enqueue("5001 update", "localhost:5001")
    pending_work_queues.enqueue("5001 update 2", "localhost:5001")
    pending_work_queues.dequeue_every_queue()
    calc.check(pending_work_queues.get_total_no_of_updates() == 0)



def add_tests(calc):
    calc.add_test(test_pending_work)