import logging


def time_calc(clock_in_hour,clock_out_hour,clock_in_min,clock_out_min,time_of_day_in,time_of_day_out):
    total_min = 0
    total_hour = 0
    total_time = 0
    if time_of_day_in.upper().strip()=='AM' and time_of_day_out.upper().strip()=='AM' or time_of_day_in.upper().strip()=='PM' and time_of_day_out.upper().strip()=='PM':
        if clock_in_hour == clock_out_hour:
            total_time = clock_out_min - clock_in_minute
            total_time = (total_time / 60.0)
        else:
            total_min = (60 - clock_in_minute) + clock_out_min
            # This is included as part of the mathematics >
            clock_in_hour += 1
            total_hour = clock_out_hour - clock_in_hour
            total_time = total_hour + (total_min / 60.0)
    elif time_of_day_in.upper().strip()=='AM' and time_of_day_out.upper().strip()=='PM':
        clock_out_hour += 12
        total_min = (60 - clock_in_min) + clock_out_min
        clock_in_hour +=1
        total_hour = clock_out_hour - clock_in_hour
        total_time = total_hour + (total_min / 60.0)
    else:
        logging.info('calculator failure')
    return total_time
