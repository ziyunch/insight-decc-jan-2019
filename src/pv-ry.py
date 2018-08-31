import sys


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
            Read and parse `predict.txt` and prepare dictionary `pred_dict`;
            Since all the predicted stock price were based on actual price for
             the same stock, the stocks for comparison in each hour are counted
              when I prepare `pred_dict` and store in `time_dict`;
            Maximum hour is also counted as `time_count`.
    Args:
        pred_file: (string) Input predicted file.
    Returns:
        pred_dict: {hour:{stock:price}} A dictionary hold every stock and its
                    price for every hour appeared in the predicted file;
        time_dict: {hour:[count, error_sum]} A dictionary hold list of the count
                    number for stock and the sum of price difference for every
                    hour appeared in the predicted file. The count numbers are
                     filled while the sum of price difference is still missing
                     (set to 0);
        time_count: (int) Maximum hour in the predicted file.
    """
    # Initialize the dictionaries
    time_dict = {}
    time_dict[0] = []
    pred_dict = {}
    pred_dict[0] = {}

    # Initialize the variable
    time_count = 0    # Use this to find maximum hour in the file
    count = 0    # Use this to count stocks in each hour

    # Parse the list
    with open(pred_file) as f:
        for line in f:
            hour, stock, price = parse_file(line)
            if hour not in pred_dict:
                time_dict[time_count] = [count, 0]
                pred_dict[hour] = {}
                time_dict[hour] = []
                time_count = hour  # Set the current max hour
                count = 0  # Reset the stock count in new hour
            pred_dict[hour][stock] = price
            count += 1  # Count
        time_dict[time_count] = [count, 0]
    return pred_dict, time_dict, time_count


def compare_actual(act_file, pred_dict, time_dict):
    """Read `actual.txt`, compare and finish up building `time_dict`
            Read and parse `actual.txt`;
            If find a stock at given hour in `pred_dict`, calculate the price
             difference between prediction and actual value and add it into
             `error_sum` to finish up building `time_dict`.
    Args:
        act_file: (string) Input predicted file
        pred_dict: {hour:{stock:price}} A dictionary hold every stock and its
                    price for every hour appeared in the predicted file
        time_dict: {hour:[count, error_sum]} A dictionary hold list of the count
                    number for stock and the sum of price difference for every
                    hour appeared in the predicted file. The count numbers are
                     filled while the sum of price difference is still missing
                     (set to 0).
    Returns:
        time_dict: {hour:[count, error_sum]} A dictionary hold list of the count
                    number for stock and the sum of price difference for every
                    hour appeared in the predicted file.
    """
    with open(act_file) as f:
        for line in f:
            hour, stock, price = parse_file(line)
            # When find in dictionary, increase sum of error of given hour by actual-predict price difference
            if hour in pred_dict:
                if stock in pred_dict[hour]:
                    time_dict[hour][1] += abs(price - pred_dict[hour][stock])

    return time_dict


def average_comparison(time_dict, window, time_count, comparison_file):
    """Calculate average error for every time window
            Start with time window from 0 to `window-1` (when window is 2, 0 to 1);
            Slide the time window by removing the previous starting hour and
             adding the current ending hour;
            Calculate average error for every time window and write into file.
    Args:
        time_dict: {hour:[count, error_sum]} A dictionary hold list of the count
                    number for stock and the sum of price difference for every
                    hour appeared in the predicted file;
        window: (int) Time window;
        time_count: (int) Maximum hour in the predicted file;
        comparison_file: (String) Output comparison file.
    """
    sum_count_window = 0
    sum_error_window = 0

    with open(comparison_file, "w") as f:
        if time_count > window:
            # Initialize sum of error and count needed for the time window 0 to `window-1`
            for i in range(1, window):
                sum_count_window += time_dict.get(i, [0, 0])[0]    # Use dictionary.get() in case hour not shown in predicted file
                sum_error_window += time_dict.get(i)[1]
            end_point = time_count - window + 2
            # Slide the time window by removing the previous starting hour and adding the current ending hour.
            for i in range(1, end_point):
                old_hour = i - 1  # set pointer as the starting hour for previous window
                sum_count_window -= time_dict.get(old_hour, [0, 0])[0]  # remove stock count for this pointer
                sum_error_window -= time_dict.get(old_hour)[1]  # remove error sum for this pointer
                new_hour = i + window - 1  # set pointer as the ending hour for current window
                sum_count_window += time_dict.get(new_hour, [0, 0])[0]  # add stock count for this pointer
                sum_error_window += time_dict.get(new_hour)[1]  # add new sum for this pointer
                if sum_count_window > 0:
                    average_error = sum_error_window / sum_count_window / 100    # Change back to dollar
                else:
                    average_error = 0
                f.write("{}|{}|{:.2f}\n".format(i, new_hour, average_error))
        else:
            if time_count > 0:
                end_point = time_count + 1
                for i in range(1, end_point):
                    sum_error_window += time_dict[i][1]
                    sum_count_window += time_dict[i][0]
                average_error = sum_error_window / sum_count_window / 100    # Change back to dollar
                f.write("{}|{}|{:.2f}\n".format(1, window, average_error))
            else:
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

    # Read `predict.txt`, get the predicted dictionary and other information
    pred_dict, time_dict, time_count = read_predict(predicted_file)

    # Read `actual.txt`, compare and finish up building `time_dict`
    time_dict = compare_actual(actual_file, pred_dict, time_dict)

    # Read time window value from `window_file`
    window_value = int(open(window_file).read())

    # Calculate average error for every time window
    average_comparison(time_dict, window_value, time_count, comparison_file)


if __name__ == "__main__":
    main()
