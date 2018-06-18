import sys
from os import path
from collections import defaultdict
from blockchain_parser.blockchain import Blockchain

DEFAULT_BITCOIN_DIR = "/home/qubes/.bitcoin/blocks"
DEFAULT_BLOCK_START = 473623
DEFAULT_BLOCK_RANGE = 2000
USE_DEFAULT_RULESET = True
DEFAULT_PATH_TO_RULESET = "./ruleset.json"
DEFAULT_PATH_TO_OUTPUT = "./genesis_file"
VERBOSE_MODE = False 

def from_sat_normalize(raw_stake):
    return raw_stake / 20000

def compute_stake(block_cursor, amount_sat):
    if block_cursor <= 399 and block_cursor >= 0:
        return amount_sat + amount_sat * 0.2
    elif block_cursor <= 799 and block_cursor > 399:
        return amount_sat + amount_sat * 0.15
    elif block_cursor <= 1199 and block_cursor > 799:
        return amount_sat + amount_sat * 0.1
    elif block_cursor <= 1599 and block_cursor > 1199:
        return amount_sat + amount_sat * 0.05
    else: return amount_sat

def verbose(msg):
    if VERBOSE_MODE: print(msg)

def progress(current, total):
    percentage = (current / total) * 100
    print("%.2f %% completed" % percentage, flush=True, end='\r')

def harvest(blockchain_obj, data_path, block_start, block_end, genesis_map):
    delta = block_end - block_start
    for cursor, block in enumerate(blockchain.get_ordered_blocks(data_path + '/index', start=block_start, end=block_end)):
        progress(cursor, delta)
        verbose("height=%d block=%s" % (block.height, block.hash))
        for tx in block.transactions:
            verbose("\ttx=%s" % tx.hash) 
            for output in tx.outputs:
                if output.script.value == 'INVALID_SCRIPT':
                    continue

                raw_stake = 0 
                normalized_stake = 0

                for address in output.addresses:
                    if address.is_p2sh():
                        raw_stake += compute_stake(cursor, output.value)
                        normalized_stake += from_sat_normalize(raw_stake)
                        genesis_map[address.address] += normalized_stake
                        verbose("\t\taddress=%s raw_stake=%.3f normalized=%.3f" % (address.address, raw_stake, normalized_stake))

                if (raw_stake > 0 and normalized_stake > 0):
                    verbose("\traw_stake=%.8f normalized=%.8f" % (raw_stake, normalized_stake))

    return genesis_map

def persist_genesis(mappings, path_to_output_file):
    with open(path_to_output_file, 'w') as out:
        for addr, stake in mappings.items():
            out.write("%s | %8f\n" % (addr, stake))



def usage(custom_msg=""):
    print("ntezos_genesis [<path_to_bitcoin_data_dir> <starting_block> <end_block> <path_to_output_file>]")
    if custom_msg: print(custom_msg)

if __name__ == "__main__":
    print("###########################################")
    print("#        Genesis block generation         #")
    print("#        by yellow_snake @ ntezos         #")
    print("#                                         #")
    print("#  other independent tools are available  #")
    print("#        use the ones you prefer.         #")
    print("###########################################")

    path_to_bitcoin_data = ""
    block_start = 0
    block_range = 0
    block_end   = 0
    path_to_output_file = ""

    if len(sys.argv) != 1 and len(sys.arg) != 5:
        usage()
        exit(1)

    elif len(sys.argv) == 5:
        path_to_bitcoin_data = sys.argv[1]
        if not os.path.isdir(path_to_bitcoin_data):
            usage("<path_to_bitcoin_dir> must be a valid/readable directory")
            exit(1)

        try: block_start = int(sys.argv[2])
        except ValueError:
            usage("<block_start> must be a positive integer")
            exit(1)

        try: block_length = int(sys.argv[3])
        except ValueError:
            usage("<block_size_interval> must be a positive integer")
            exit(1)

        block_end = block_start + block_size_interval

        path_to_output_file = sys.argv[4]
        if path_to_output_file == "":
            usage("<path_to_output_file> must not be empty!")
            exit(1)

    else:
        path_to_bitcoin_data = input("Path to local bitcoind data directory [default: %s]:" % DEFAULT_BITCOIN_DIR) or DEFAULT_BITCOIN_DIR
        if path_to_bitcoin_data == DEFAULT_BITCOIN_DIR:
            print("Default path selected (%s)" % path_to_bitcoin_data)

        try: block_start = int(input("Block start [default: %d]:" % DEFAULT_BLOCK_START))
        except ValueError: block_start = DEFAULT_BLOCK_START

        if block_start == DEFAULT_BLOCK_START:
            print("Default block start selected (%d)" % block_start)

        try: block_range = int(input("Length in blocks [default: %d #blocks]:" % DEFAULT_BLOCK_RANGE))
        except ValueError: block_range = DEFAULT_BLOCK_RANGE

        if block_range == DEFAULT_BLOCK_RANGE:
            print("Default block range selected (%d)" % block_range)

        path_to_output_file = input("Path to ouptut [default: %s]:" % DEFAULT_PATH_TO_OUTPUT) or DEFAULT_PATH_TO_OUTPUT
        if path_to_output_file == DEFAULT_PATH_TO_OUTPUT:
            print("Default output path selected (%s)" % path_to_output_file)

        block_end = block_start + block_range

    genesis_map = defaultdict(float)
    blockchain = Blockchain(path_to_bitcoin_data)
    genesis_map = harvest(blockchain, path_to_bitcoin_data, block_start, block_end, genesis_map)
    
    if VERBOSE_MODE:
        for addr, stake in genesis_map.items():
            verbose("%s | %.8f" % (addr, stake))

    verbose("stats:")
    verbose("num wallets=%d" % len(genesis_map))

    persist_genesis(genesis_map, path_to_output_file)
