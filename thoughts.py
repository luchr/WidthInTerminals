#!/bin/python3
# vim:ts=4:sw=4:fdm=indent:cc=79:

'''
Some thoughts about strings and their visual representations in terminals.
'''

from io import StringIO
from textwrap import dedent

NL = '\n'
SKIN_TYPE = ( # Fitzpatrick
    '\U0001f3fb', '\U0001f3fb', '\U0001f3fc',
    '\U0001f3fd', '\U0001f3fe', '\U0001f3ff')

ZWJ = '\u200d' # zero width joiner

VARSEL15 = '\ufe0e'
VARSEL16 = '\ufe0f'

def get_codepoints(string):
    '''return the codepoints of the string in simple "<hex>" notation.'''
    return ' '.join(f"{ord(character):X}" for character in str(string))

def describe_string(string):
    '''return codepoints and the string. Try alignment.'''
    return f"{get_codepoints(string):60s}: {string}"

def describe_ecgs(string, boundaries_delta, widths):
    '''return ECG informations for boundaries.'''
    last_pos = 0
    with StringIO() as sio:
        sio.write(
            f"      code points              ┃#cp ┃ TCW  ┃ ECG {NL}"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━╇━━━━━━╇━━━━╸{NL}")

        for (delta, width) in zip(boundaries_delta, widths):
            next_pos = last_pos + delta
            part = string[last_pos:next_pos]
            sio.write(
                    f"{get_codepoints(part):30s} "
                    f"│ {len(part):2d} │   {width:2d} │ {part}{NL}")
            last_pos = next_pos
        return sio.getvalue()

def codepoints_width_problem():
    '''codepoints do *not* have a well-defined width.'''
    wrench = '\U0001f527'
    woman = '\U0001f469'

    print(dedent(f'''
    ## There is no "the terminal width" for a unicode codepoint

    Let's look at the following codepoint:

    ```
    {describe_string(wrench)}
    ```

    Looks like this wrench `{wrench}` codepoint has some positive width.

    But wait. If it's attached (with the Zero Width Joiner U+200D) to the
    codepoint `{woman}` then you get:

    ```
    {describe_string(woman)}
    {describe_string(woman + wrench)}
    {describe_string(woman + ZWJ + wrench)}
    ```

    In the last example the wrench is used to "modify" the `{woman}` in order
    to produce a female mechanic.
    In this context the wrench `{wrench}` has width 0.

    Conclusion:

    >
    > The (terminal-)width of a codepoint may depend on the context.
    >

    So the idea to look for a function `width_of_codepoint(code_point)`
    does not make any sense at all.

    Between the first codepoint and the ZWJ U+200D there may also occur
    a Fitzpatrick skin tone (which then has in this context also width 0):

    ```
    {describe_string(woman + SKIN_TYPE[0] + ZWJ + wrench)}
    {describe_string(woman + SKIN_TYPE[1] + ZWJ + wrench)}
    {describe_string(woman + SKIN_TYPE[2] + ZWJ + wrench)}
    {describe_string(woman + SKIN_TYPE[3] + ZWJ + wrench)}
    {describe_string(woman + SKIN_TYPE[4] + ZWJ + wrench)}
    {describe_string(woman + SKIN_TYPE[5] + ZWJ + wrench)}
    ```


    '''))

def ecg_intro():
    '''Extended Grapheme Clusters'''
    url_ecg = (
        'https://unicode.org/reports/tr29/' +
        '#Table_Combining_Char_Sequences_and_Grapheme_Clusters')

    print(dedent(f'''
    ## Extended Grapheme Cluster

    Are there other objects where "width" might be well-defined?

    Instead of focusing on the codepoints an other idea is to look for
    visual units: one or more codepoints which are perceived as one
    unit. Obviously that's not a definition.

    The Unicode standard defines a conecpt called "extended grapheme
    cluster", see [Unicode UAX #29]({url_ecg}). Let's call them ECG.



    '''))

def tr11():
    '''uax #11 won't help.'''

    print(dedent(f'''
    ## The width of a ECG according to UAX 11

    Reading in the Unicode specs one might think
    [UAX #11](https://unicode.org/reports/tr11/)
    might help. It defines(!) a width for ECG.

    **BUT!**  _BUT!_ But! In general the so defined width has nothing to do
    with the number of columns monospaced fonts (and/or terminal emulators)
    use to render an ECG.

    Let's cite Manish Goregaokar who wrote
    [unicode_rs/unicode_width](https://github.com/unicode-rs/unicode-width)
    to determine the width according to UAX 11:

    > NOTE: The computed width values may not match the
    >       actual rendered column width. 

    For the female mechanic above the UAX 11 width will be larger than 2.


    '''))

def needed():
    '''So many "problems", where are the "solutions".'''

    rivo_url = 'https://pkg.go.dev/github.com/rivo/uniseg#hdr-Monospace_Width'

    print(dedent(f'''
    ## A new hope

    A new hope is needed if one really wants to have the
    terminal-column-width (TCW). At the moment I cannot find a "standard"
    or even a "definition" which tries to cover the TCW-problem.

    There are several solutions and requests for solutions, like

    * https://github.com/kovidgoyal/kitty/issues/3810
    * https://github.com/jquast/wcwidth/issues/39

    Just to name a few.

    The most "sophisticated" attempt I can find is:
    [rivo/uniseg: Monospace Width]({rivo_url})


    '''))

def align_trunc():
    '''whishes for alignment and truncation'''
    example = (
        'o\u20d7, e\u0308, \u00eb and \U0001f34e are all ECG\U0001f448' +
        SKIN_TYPE[3])
    example_16 = example[0:18]
    example_14 = example[0:14]
    example_15 = example[0:15]
    apple = '\U0001f34e'

    print(dedent(f'''
    ## Whishes

    If one wants to align strings in the terminal and or truncate
    them at a given column then typically the information of the TCW of the
    whole string is not enough: Why? Becasue one typically wants to know:
    What code points are used for the first 7 visual columns?

    Take the string "{example}" and let's use a "ruler":

    ```
              1         2
    0123456789012345678901234567
    ││││││││││││││││││││││││││││
    {example}
    ```

    Here are the codepoints:
    {get_codepoints(example)}

    A typical question: How many codepoints do I need, if I want to
    truncate this string at the column number 16? [So that the result
    has TCW of 17.] Here the answer is:
    Use the codepoints range(0, 18) [0:18].

    ```
              1
    01234567890123456
    │││││││││││││││││
    {example_16}
    ```

    And what about column number 12? 

    ```
              1
    01234567890123
    ││││││││││││││
    {example_14}
    {example_15}
    ```

    Either you take the codepoints 0:14 or 0:15. In the first case the
    columns 0 to 11 are occupied and in the second case the columns 0 to 13
    are used. It is not possible to cut the apple in two halfs. Ohh. What
    a bold claim! Wait, unicode makes this possible (sometimes).
    Let's take a small detour for the apple:

    ```
    {describe_string(apple)}
    {describe_string(apple + VARSEL16)}
    {describe_string(apple + VARSEL15)}
    ```

    In some terminals you'll see:

    ![A smaller apple ...](./apple_varsel.png)

    OK. End of the detour.

    What can be done to answer such questions:

    A function of the type

    ```
      width_of_next_ecg(string, start_pos) -> (width, next_pos)
    ```

    may do the job. As input you give a string and the starting position
    where to look for the next ECG. This function is not looking "backwards".
    It does *not* scan what is before start_pos. It looks "forward"
    starting at start_pos and computes the width for the next ECG, returns
    this width and how many codepoints went into this ECG. So that
    next_pos can be used to get the informations of the next ECG.

    ```'''))

    print(describe_ecgs(example,
        (2,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2),
        (1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,2)))
    print('```')


def main():
    '''show introduction, some examples and more.'''

    print(dedent(f'''
    # Some thoughts about strings and their visual width in terminals

    In this context "string" means a list of unicode codepoints.
    And "terminals" means terminal emulators.
    '''))

    codepoints_width_problem()
    ecg_intro()
    tr11()
    needed()
    align_trunc()


main()

# EOF
