I'm assuming single threaded system or else timestamps will have to be (t, i) where t is the time at which it is sent
and i is the thread id, to implement this correctly, i will need a priority queue

thread i has
queue
function to send messages (requests and replies)
function to check and receive messages (requests and replies)

what thread i does
while in non-critical or send-request or waiting-for-same-time-requests or waiting-to-enter
    check for release from top of queue, pop if received
while in non-critical:
    check for new requests, send reply for each and add to queue in the order they came.
    move to either non-critical or send-request state
while in send-request:
    receive requests (these will be from the previous timestep), add to queue, send request
    empty out reply array
    move to wait-for-same-time-requests
while in wait-for-same-time-requests:
    get requests from all thread j < i, add all to queue, add own request to queue, get requests from thread j > i, add all to queue
    in this state we can't receive replies since threads have only just received them
    move to waiting-to-enter
while in waiting-to-enter:
    receive replies and switch them on in the array
    if self at top and all replies received move to critical
    else stay in waiting-to-enter
while in critical:
    check for new requests, add to queue, and reply to them
    stay in critical or move to exit
while in exit:
    send release to all
    move to non-critical


if we're using processes:
states non-critical, waiting, critical, exit
non-critical

Requests for CS are executed in the increasing order of timestamps and time
is determined by logical clocks.
Every site Si keeps a queue, request queuei
, which contains mutual exclusion
requests ordered by their timestamps.
This algorithm requires communication channels to deliver messages the
FIFO order.
