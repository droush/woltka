#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# Copyright (c) 2020--, Qiyun Zhu.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""Functions for classifying query sequences by assigning their subjects to a
hierarchical classification system.
"""

from operator import itemgetter
from collections import defaultdict

from .util import count_list
from .tree import find_rank, find_lca


def assign_none(subs, uniq=False):
    """Assign query to subjects without using a classification system.

    Parameters
    ----------
    subs : set of str
        Subjects.
    uniq : bool, optional
        Assignment must be unique.

    Returns
    -------
    str or dict
        Unique subject or list of subjects.
    """
    try:
        sub, = subs
        return sub
    except ValueError:
        return None if uniq else list(subs)


def assign_free(subs, tree, root=None, subok=False):
    """Assign query based on a classification system in a rank-free manner.

    Parameters
    ----------
    subs : set of str
        Subjects.
    tree : dict
        Hierarchical classification system.
    root : str, optional
        Root identifier.
    subok : bool, optional
        Allow assignment to subjects.

    Returns
    -------
    str or None
        Unique assignment.
    """
    try:
        sub, = subs
        return sub if subok else (tree[sub] if sub in tree else None)
    except ValueError:
        lca = find_lca(subs, tree)
        return None if lca == root else lca


def assign_rank(subs, rank, tree, rankdic, root=None, major=None, above=False,
                uniq=False):
    """Assign query to a given rank in a classification system.

    Parameters
    ----------
    subs : set of str
        Subjects.
    rank : str
        Target rank.
    tree : dict
        Hierarchical classification system.
    rankdic : dict
        Rank dictionary.
    root : str, optional
        Root identifier.
    major : float, optional
        Majority-rule assignment threshold.
    above : bool, optional
        Allow assignment above rank.
    uniq : bool, optional
        Assignment must be unique.

    Returns
    -------
    str or list or None
        Unique assignment or list of assignments.

    TODO
    ----
    Combine major and above.
    """
    taxa = [find_rank(x, rank, tree, rankdic) for x in subs]
    tset = set(taxa)
    if len(tset) == 1:
        return taxa[0]
    elif major:
        return majority(taxa, major)
    elif above:
        if None in tset:
            return None
        lca = find_lca(tset, tree)
        return None if lca == root else lca
    elif uniq:
        return None
    else:
        return taxa


def count_taxa(subque, taxque, sizes=None):
    """Count occurrences of taxa in a map.

    Parameters
    ----------
    subque : iterable of frozenset
        Subject(s) queue to manipulate.
    taxque : iterable of str or list
        Taxon(a) assigned to each query.
    sizes : dict, optional
        Subject size dictionary.

    Returns
    -------
    dict of dict of int
        Map of taxon to subject to count.

    See Also
    --------
    count_taxa_strat

    Notes
    -----
    Subjects (frozenset) and taxa (list) are precise matches. This is ensured
    by the iteration stability of Python sets / frozensets. See:

    .. _Source:
        https://stackoverflow.com/questions/15479928/why-is-the-order-in-
        dictionaries-and-sets-arbitrary
    """
    is_size, get_size = (True, sizes.get) if sizes else (False, None)
    res = defaultdict(int)
    for subs, taxa in zip(subque, taxque):
        if not taxa:
            continue
        # there's only one taxon (a string)
        # !!!!!!!!!!!!! warning
        try:
            res[taxa] += sum(map(get_size, subs)) / len(subs) if is_size else 1
        # taxa is a list (each subject corresponds to one taxon)
        except TypeError:
            k = 1 / len(list(filter(None, taxa)))
            for taxon, sub in zip(taxa, subs):
                if not taxon:
                    continue
                res[taxon] += get_size(sub) * k if is_size else k
    return res


def count_taxa_strat(qryque, subque, taxque, strata, sizes=None):
    """Stratify taxa in a map and count occurrences.

    Parameters
    ----------
    qryque : iterable of str
        Query sequences.
    subque : iterable of frozenset
        Subject(s) queue to manipulate.
    taxque : iterable of str or list
        Taxon(a) assigned to each query.
    strata : dict
        Query-to-stratum map for stratification.
    sizes : dict, optional
        Subject size dictionary.

    Returns
    -------
    dict of dict of int
        Map of (stratum, taxon) to subject to count.

    See Also
    --------
    count_taxa
    """
    is_size, get_size = (True, sizes.get) if sizes else (False, None)
    res = defaultdict(int)
    for query, subs, taxa in zip(qryque, subque, taxque):
        if not taxa or query not in strata:
            continue
        stratum = strata[query]
        try:
            res[(stratum, taxa)] += sum(map(get_size, subs)) / len(
                subs) if is_size else 1
        except TypeError:
            k = 1 / len(list(filter(None, taxa)))
            for taxon, sub in zip(taxa, subs):
                if not taxon:
                    continue
                res[(stratum, taxon)] += get_size(sub) * k if is_size else k
    return res


def majority(taxa, th=0.8):
    """Select taxon from list by majority rule.

    Parameters
    ----------
    taxa : list of str
        Input taxon list.
    th : float, optional
        Threshold of majority, range = (0.5, 1.0].

    Returns
    -------
    str or None
        Selected taxon.
    """
    for taxon, n in sorted(count_list(taxa).items(), key=itemgetter(1),
                           reverse=True):
        return taxon if n >= len(taxa) * th else None
