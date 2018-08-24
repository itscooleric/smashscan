

# A custom filter that works on an int array that represents the timeline of 
# labels (stages) found by tfnet. (-1) represents that no stage was found. The 
# goal of this filter is to fill in small time segment holes, while also 
# filtering out small time segments. 
def get_clean_hist(dirty_hist_in, step_size):
    # The time required for a time segment to be considered gameplay. Assumes
    # the game is captured as 30fps, and the minimum match length is 30s.
    state_length_thresh = int(30 * (30 / step_size))

    # Tunable parameter
    differ_thresh = 5
    
    # Add some no-stage found states at the end of dirty_hist to allow the
    # filter defined below work at the end of the list. This fix is necessary
    # when the match ends too close (with differ_thresh) to the end of the 
    # video. These states will be removed after the filtering is complete. 
    # The function input is not directly modified since arrays are mutable.
    dirty_hist = dirty_hist_in + [-1]*differ_thresh

    # Assume that the history timeline has no stages present (-1).
    clean_hist = [-1] * len(dirty_hist)

    # Used to store the stage (state) currently present. It will remain the
    # current_state unless differ_thresh number of timesteps differ in a row.
    current_state = -1

    # Used to store the stage (state) that most recently differed from the 
    # current state. current_state will become differ_state if differ_thresh
    # number of timestamps are consistent in a row.
    differ_state = -1  

    # The counter used to count the number of times the timestep differs. If
    # the timestep differs but not consistently (different from differ_state),
    # current_state will become the no-stage found state (-1).
    differ_count = 0

    # The counter used to count the number of times the timestep differs. 
    # However, if the timestep consistently differs to differ_state, 
    # current_state will become differ_state once differ_thresh is met.
    differ_const_count = 0

    # Iterate through dirty_hist and perform the filtering defined above.
    for i in range(0, len(dirty_hist)):
        if current_state != dirty_hist[i]:
            if differ_state == dirty_hist[i]:
                differ_count += 1
                differ_const_count += 1
            else:
                differ_count += 1
                differ_const_count = 1
                differ_state = dirty_hist[i]

            if differ_const_count == differ_thresh:
                differ_const_count = 0
                current_state = differ_state
                clean_hist[i-(differ_thresh-1):i] = \
                    [current_state] * (differ_thresh-1)
            elif differ_count == differ_thresh:
                differ_count = 0
                current_state = -1
                clean_hist[i-(differ_thresh-1):i] = \
                    [current_state] * (differ_thresh-1)
        else:
            differ_count = 0
            differ_const_count = 0
            differ_state = dirty_hist[i]
        clean_hist[i] = current_state

    # Remove the no-stage states inserted at the input of the filter.
    dirty_hist = dirty_hist[:-differ_thresh]
    clean_hist = clean_hist[:-differ_thresh]

    # print (dirty_hist)
    # print (clean_hist)
    # print (get_match_ranges(clean_hist))
    return clean_hist


# TODO write comment
def get_match_ranges(clean_hist):
    current_state = -1
    start_timestep = 0
    match_range_list = list()

    # End fix
    used_hist = clean_hist + [-1]

    for i in range(0, len(used_hist)):
        if used_hist[i] != -1 and current_state == -1:
            current_state = used_hist[i]
            start_timestep = i
        elif used_hist[i] != current_state and current_state != -1:
            current_state = -1
            match_range_list.append((start_timestep, i - 1))

    return match_range_list