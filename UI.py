# Draw pre-round screen
def pre_round(frame, round):
    return frame


# Draw countdown screen
def countdown(frame, countdown):
    return frame


# Draw UI for when the round is running
# Note: target is in world space
# Note: p1 and p2 are coordinates in pixel space
def playing_round(frame, round, round_time, target, p1_coords, p2_coords):
    return frame


# Draw the end of round screen
def post_round(frame, countdown, p1_score, p2_score):
    return frame


# Draw the end game screen that displays who the winner is
def end_game(frame, p1_score, p2_score):
    return frame

