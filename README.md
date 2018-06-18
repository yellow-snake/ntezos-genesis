### ntezos_genesis

One implementation of a p2sh:allocation mapping script.

`ntezos_genesis` harvest an arbitrary block range and apply an arbitrary rule set to determine a potential allocation for each p2sh address.
By default, the rule set it follows is the one of the Tezos fundraiser. You can easily modify the script to apply a rule set of your own choosing (see `compute_stake` and `from_sat_normalize`).


```
ntezos_genesis [<path_to_bitcoin_data_dir> <starting_block> <end_block> <path_to_output_file>]
```

I recommend that you pipe the output file to `sort` in order to "standardize" comparisons.
Note that the current output is a bit raw (unrounded floating numbers with long tails, "dust" allocations).

## p2sh genesis hash:

c6eacdee8f2b95b5263e13c97e659ac0b80830ff6081ff238b986e768073879d  sorted_genesis_file
