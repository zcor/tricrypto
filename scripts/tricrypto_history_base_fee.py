import csv
import math
from datetime import datetime

from brownie import Contract


def main():
    block_start = 8500000
    block_end = 9027939
    target_num_rows = 100
    tricrypto = Contract("0x6e53131f68a034873b6bfa15502af094ef0c5854")  # Base TriCrypto

    delay = (block_end - block_start) / target_num_rows
    block = block_start
    est_blocks = (block_end - block) / delay
    print(f"Expect {est_blocks:.0f} rows worth of data")

    data = []  # Initialize an empty list to collect data
    counter = 0
    function_names = [
        "fee",
        "virtual_price",
        "A",
        "gamma",
        "fee_gamma",
        "D",
        "lp_price",
        "mid_fee",
        "out_fee",
        "xcp_profit",
        "xcp_profit_a",
    ]

    while block < block_end:
        counter += 1
        block += math.floor(delay)
        if block > block_end:
            break

        price_oracle = [
            tricrypto.price_oracle(0, block_identifier=block),
            tricrypto.price_oracle(1, block_identifier=block),
        ]
        price_scale = [
            tricrypto.price_scale(0, block_identifier=block),
            tricrypto.price_scale(1, block_identifier=block),
        ]

        more_data = []
        for func_name in function_names:
            try:
                func = getattr(tricrypto, func_name)
                more_data.append(func(block_identifier=block))
            except Exception as e:
                print(f"Error calling {func_name} with block {block}: {e}")
                more_data.append(None)

        # Append the data to the data list
        data.append([block] + price_oracle + price_scale + more_data)
        print(
            f"Row {counter}/{est_blocks:.0f}, Block {block} ({block_start} - {block_end})\n",
            more_data,
        )

    # Generate the current date and time string for the file name
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"tricrypto_base-{current_datetime}.csv"

    # Write the data to the CSV file
    headers = [
        "block",
        "price_oracle_0",
        "price_oracle_1",
        "price_scale_0",
        "price_scale_1",
    ] + function_names

    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)  # Write data rows
