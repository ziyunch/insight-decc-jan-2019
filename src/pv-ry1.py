import sys
from collections import deque
from decimal import Decimal, ROUND_HALF_UP


def round(n, m=0):
    return float(Decimal(n).quantize(Decimal('0.{}'.format('0'*m)), ROUND_HALF_UP))

def parse_file(line):
    """Parse line for input
    Args:
        line: (string) Input.
    Returns:
        hour: (int) A integer designating the hour;
        stock: (string) ID of the stock;
        price: (int) Stock price of the given hour, in pennies.
    """
    line_split = line.strip().split("|")
    # Parse the list
    hour = int(line_split[0])  # A integer designating the hour
    stock = line_split[1]  # ID of the stock
    price = int(float(line_split[2]) * 100)  # Stock price of the given hour, change currency into penny

    return hour, stock, price


def read_predict(pred_file):
    """Read `predict.txt`, get the predicted dictionary and other information
            Read and parse `predict.txt` and prepare dictionary `pred_dict`.
    Args:
        pred_file: (string) Input predicted file.
    Returns:
        pred_dict: {hour:{stock:price}} A dictionary hold every stock and its
                    price for every hour appeared in the predicted file.
    """
    # Initialize the dictionaries
    pred_dict = {}
    pred_dict[0] = {}

    # Parse the list, O(n)
    with open(pred_file) as f:
        for line in f:
            hour, stock, price = parse_file(line)
            if hour not in pred_dict:
                pred_dict[hour] = {}
            pred_dict[hour][stock] = price
    return pred_dict


def compare_actual(act_file, pred_dict):
    """Read `actual.txt`, compare and build `time_dict`
            Read and parse `actual.txt`;
            If find a stock at given hour in `pred_dict`, calculate the price
             difference between prediction and actual value and add it into
             `error_sum` in the deque `time_deque`; For others, add [0,0]
            Maximum hour is also counted as `time_count`.

    Args:
        act_file: (string) Input predicted file
        pred_dict: {hour:{stock:price}} A dictionary hold every stock and its
                    price for every hour appeared in the predicted file
    Returns:
        time_deque: ([count, error_sum]) A deque hold list of the count
                    number for stock and the sum of price difference for every
                    hour appeared in the predicted file.
        time_count: (int) Maximum hour in the predicted file.
    """

    # Initialize the deque
    time_deque = deque()

    count = 0
    error_sum = 0
    time_count = 0
    with open(act_file) as f:
        for line in f:    # O(n)
            hour, stock, price = parse_file(line)
            while time_count < hour:
                time_deque.append([count, error_sum])
                count = 0    #  Reset the stock count in new hour
                error_sum = 0    # Reset the sum of error in new hour
                time_count += 1 # Set the current max hour
            # When find in dictionary, increase sum of error of given hour by actual-predict price difference
            if hour in pred_dict:
                if stock in pred_dict[hour]:
                    count += 1
                    error_sum += abs(price - pred_dict[hour][stock])
    time_deque.append([count, error_sum])

    return time_deque, time_count


def average_comparison(time_deque, window, time_count, comparison_file):
    """Calculate average error for every time window
            Start with time window from 0 to `window-1` (when window is 2, 0 to 1);
            Slide the time window by removing the previous starting hour and
             adding the current ending hour;
            Calculate average error for every time window and write into file.
    Args:
        time_deque: ([count, error_sum]) A deque hold list of the count
                    number for stock and the sum of price difference for every
                    hour appeared in the predicted file.
        window: (int) Time window;
        time_count: (int) Maximum hour in the predicted file;
        comparison_file: (String) Output comparison file.
    """

    # Initialize the deque
    window_deque = deque()

    sum_count_window = 0
    sum_error_window = 0

    with open(comparison_file, "w") as f:
        if time_count > window:
            # Initialize sum of error and count needed for the time window 0 to `window-1`
            for i in range(0, window):    # O(n)
                temp = time_deque.popleft()
                window_deque.append(temp)    # Store the data in a smaller deque for further use
                sum_count_window += temp[0]
                sum_error_window += temp[1]
            end_point = time_count - window + 2
            # Slide the time window by removing the previous starting hour and adding the current ending hour.
            for i in range(1, end_point):
                temp = window_deque.popleft()    # pop out the data in the starting hour
                sum_count_window -= temp[0]  # remove stock count for this moment
                sum_error_window -= temp[1]  # remove error sum for this moment
                temp = time_deque.popleft()    # pop out the data in the ending hour
                window_deque.append(temp)    # store it in a smaller deque for further use
                sum_count_window += temp[0]  # add stock count for this moment
                sum_error_window += temp[1]  # add new sum for this moment
                new_hour = i + window - 1
                if sum_count_window > 0:
                    average_error = sum_error_window / sum_count_window / 100    # Change back to dollar
                    f.write("{}|{}|{:.2f}\n".format(i, new_hour, average_error))
                else:    # No predicted stock price in given time window
                    f.write("{}|{}|NA\n".format(i, new_hour))
        else:
            if time_count > 0:    # Predicted hour not enough for one window
                end_point = time_count + 1
                for i in range(1, end_point):
                    temp = time_deque.popleft()
                    sum_error_window += temp[1]
                    sum_count_window += temp[0]
                average_error = sum_error_window / sum_count_window / 100    # Change back to dollar
                f.write("{}|{}|{:.2f}\n".format(1, window, average_error))
            else:    # No predicted stock price
                f.write("{}|{}|NA\n".format(1, window))


def main():
    if len(sys.argv) != 5:
        print("Four arguments are expected: [window.txt], [actual.txt], [predicted.txt], [comparison.txt]")
        exit(1)

    # Input
    actual_file = sys.argv[2]
    predicted_file = sys.argv[3]
    window_file = sys.argv[1]
    comparison_file = sys.argv[4]

    # Read `predict.txt`, get the predicted dictionary and other information, O(n)
    pred_dict = read_predict(predicted_file)

    # Read `actual.txt`, compare and build `time_deque`, O(n)
    time_deque, time_count = compare_actual(actual_file, pred_dict)

    # Read time window value from `window_file`, O(1)
    window_value = int(open(window_file).read())

    # Calculate average error for every time window, O(n)
    average_comparison(time_deque, window_value, time_count, comparison_file)


if __name__ == "__main__":
    main()
