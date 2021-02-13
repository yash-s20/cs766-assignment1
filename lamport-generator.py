"""
Author: Yash Sharma
"""

import sys


n = int(sys.argv[1])
PART_1 = f"""-- Author: Yash Sharma

MODULE thread(i, t, request, reply, release)
VAR
    state : {{non_critical, send_request, waiting_to_enter, critical, exit}};
    request_queue : array 0..{n - 1} of -1..{n-1}; -- atmost n requests at a time, and -1 for null.
    next_request_to_process : 0..{n-1}; -- index to the above queue for top, and empty if request_queue[next_request_to_process mod n] is -1
JUSTICE running;
COMPASSION (state = critical, state = exit);"""

delim = "\n    "
PART_2 = f"""
DEFINE
    all_replies_received := {" & ".join([f"(reply[i][{j}] | i = {j})" for j in range(n)])}; -- this will be n conjunctions for n threads.
ASSIGN
    init(state) := non_critical;
    init(next_request_to_process) := 0; -- this is where the first entry to the queue will go
    -- for each 0..n-1 n threads
    {delim.join([f"init(request_queue[{j}]) := -1;" for j in range(n)])}"""

PART_3 = f"""
    next(state) := case
                    state = non_critical : {{non_critical, send_request}};
                    state = send_request : waiting_to_enter;
                    state = waiting_to_enter & (request_queue[next_request_to_process] = i) & (all_replies_received) : critical;
                    state = waiting_to_enter : waiting_to_enter;
                    state = critical : {{critical, exit}};
                    state = exit : non_critical;
                   esac;
    next(t) := case
                (state = send_request) : (t + 1) mod {n};
                TRUE : t;
               esac;"""

release_jj = "\n".join([f"""    next(release[{j}][{j}]) := case
                            i = {j} & (next(state) = exit) : TRUE;
                            i = {j} : FALSE;
                            TRUE: release[{j}][{j}];
                           esac;""" for j in range(n)])

release_jk = "\n".join([f"""    next(release[{j}][{k}]) := case
                            (i = {j}) : FALSE;
                            (i = {k}) & (next(state) = exit) : TRUE;
                            TRUE: release[{j}][{k}];
                           esac;""" for j in range(n) for k in range(n) if j != k])

PART_4 = f"""
    -- first doing release[j][j]
{release_jj}
    -- next all release[i'][j'] j' != i'
    -- release[i][j] would be made true by thread j after leaving critical, so make it false (next_request_to_process will handle it)
    -- release[j][i] has to be made true when exiting.
{release_jk}"""

release_code = "\n".join([f"""                                        (request_queue[(next_request_to_process + {j}) mod {n}] != -1) & (release[i][request_queue[(next_request_to_process + {j}) mod {n}]]) : (next_request_to_process + {j + 1}) mod {n};"""
                          for j in reversed(range(n))])

PART_5 = f"""
    next(next_request_to_process) := case
                                        (request_queue[next_request_to_process] = -1) : next_request_to_process; -- empty queue
{release_code}
                                        TRUE : next_request_to_process;
                                     esac;

"""

request_jj = "\n".join([f"""    next(request[{j}][{j}]) := case
                            (i = {j}) & (state = send_request) : t;
                            (i = {j}) : -1;
                            TRUE: request[{j}][{j}];
                           esac;""" for j in range(n)])

request_jk = "\n".join([f"""    next(request[{j}][{k}]) := case
                            (i = {k}) & (state = send_request) : t;
                            (i = {j}) : -1;
                            TRUE: request[{j}][{k}];
                           esac;""" for j in range(n) for k in range(n) if j != k])
PART_6 = f"""
    -- next(request[j][j]) := case
    --                         (i = j) & (state = send_request) : t;
    --                         (i = j) : -1;
    --                         TRUE: request[j][j];
    --                        esac;
{request_jj}

    -- next(request[j][k]) := case
    --                         (i = k) & (state = send_request) : t; -- send request
    --                         (i = j) : -1; -- request will be acknowledged if process is active
    --                         TRUE: request[j][k]; -- irrelevant.
    --                        esac;
{request_jk}"""

reply_jj = "\n".join([f"""    next(reply[{j}][{j}]) := case
                            (i = {j}) : FALSE;
                            TRUE: reply[{j}][{j}];
                         esac;""" for j in range(n)])

reply_jk = "\n".join([f"""    next(reply[{j}][{k}]) := case
                            (i = {j}) & (all_replies_received) & (next(state) = critical) : FALSE;
                            (i = {j}) : reply[{j}][{k}];
                            (i = {k}) & (request[i][{j}] != -1) : TRUE;
                            TRUE: reply[{j}][{k}];
                         esac;""" for j in range(n) for k in range(n) if j != k])

PART_7 = f"""


{reply_jj}


    -- next(reply[j][k]) := case
    --                         (i = j) & (all_replies_received) & (next(state) = critical) : FALSE; -- done with replies
    --                         (i = j) : reply[0][1]; -- not done with it yet, or not needed
    --                         (i = k) & bool (request[i][j]) : TRUE; -- send reply for request
    --                         TRUE: reply[j][k]; -- leave it as it
    --                      esac;
{reply_jk}"""


def check_k(j):
    return "\n".join(
        [f"""                                (request[i][{k}] != -1) & (request[i][{k}] = {j}) : {k};""" for k in
         range(n)])


queue_j = "\n".join([f"""    next(request_queue[{j}]) := case
{check_k(j)}
                                request_queue[{j}] = -1: -1;
                                release[i][request_queue[{j}]] : -1;
                                TRUE: request_queue[{j}];
                              esac;""" for j in range(n)])

PART_8 = f"""

    -- queueing : requests are accumulated in request[i] array
    -- next(request_queue[j]) := case
    --                         for each k
    --                         (request[i][k] != -1) & (request[i][k] = j) : k;
    --                         request_queue[j] = -1: -1;
    --                         release[i][request_queue[j]] : -1;
    --                         TRUE: request_queue[j];
    --                         esac;
{queue_j}
LTLSPEC G (state = waiting_to_enter -> F state = critical)

"""

thread_defn = "\n".join(
    [f"""    t{j + 1} : process thread({j}, timestamp, request_channel, reply_channel, release_channel);""" for j in
     range(n)])

request_defn = "\n".join([f"""    init(request_channel[{j}][{k}]) := -1;""" for j in range(n) for k in range(n)])
reply_defn = "\n".join([f"""    init(reply_channel[{j}][{k}]) := FALSE;""" for j in range(n) for k in range(n)])
release_defn = "\n".join([f"""    init(release_channel[{j}][{k}]) := FALSE;""" for j in range(n) for k in range(n)])


mutual_exclusion = " | ".join([f"""( t{j + 1}.state = critical & t{k + 1}.state = critical )""" for j in range(n) for k in range(n) if j < k])
PART_9 = f"""
MODULE main
VAR
    timestamp: 0..{n-1};
    request_channel : array 0..{n - 1} of array 0..{n - 1} of -1 .. {n-1};
    reply_channel : array 0..{n - 1} of array 0..{n - 1} of boolean;
    release_channel : array 0..{n - 1} of array 0..{n - 1} of boolean;
    -- each channel is a n x n matrix.
    -- when thread i needs to send a request, it will set t to the ith number from each array in the request_channel matrix. then put itself in the queue.
    -- to look for requests, thread i will read all numbers from request_channel[i], any for any that are 1, send a reply to that thread.
    -- when thread i is sending a reply to thread j it will set 1 to reply_channel's jth array's ith element.
    -- when looking for replies from other threads, simply make sure count reply_channel[i] (array) == n-1.
    -- when releasing critical section, simply put ith bit of each array in release channel to 1.
    -- if j is at the top of the array, look for release_channel[i][j], if true, pop the queue, and set it to false.
{thread_defn}

ASSIGN
    init(timestamp) := 0;
{request_defn}
{reply_defn}
{release_defn}
LTLSPEC
    G ! ({mutual_exclusion})"""

print(PART_1 + PART_2 + PART_3 + PART_4 + PART_5 + PART_6 + PART_7 + PART_8 + PART_9)
