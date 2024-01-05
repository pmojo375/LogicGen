def findAndReplace(text, words_to_replace, replacement_words):
    """
    Finds and replaces words in a string with other words.

    Args:
        text: The string to search through.
        words_to_replace: A list of words to replace.
        replacement_words: A list of lists containing the words to replace the words_to_replace with.

    Returns:
        A string with the words replaced.
    """

    if len(words_to_replace) == len(replacement_words):
        for i in range(len(words_to_replace)):
            text = text.replace(words_to_replace[i], replacement_words[i])
    else:
        raise ValueError(
            'words_to_replace and replacement_words must be the same length.')

    return text

def faultGen(parent_tags: list, fault_tag: list, word_start: int, bit_start: int, child_tags: list = None):
    # outputs XIC(ParentTag.ChildTag)OTL(FaultTag)[Word].Bit);   ') or omits the child tag if its none for each parent tag

    output = ''

    bit = int(bit_start)
    word = int(word_start)

    for parent_tag in parent_tags:
        if child_tags == None:
            output = (
                f'{output}XIC({parent_tag})OTL({fault_tag}[{word}].{bit});   ')
        else:
            for child_tag in child_tags:
                output = (
                    f'{output}XIC({parent_tag}.{child_tag})OTL({fault_tag}[{word}].{bit});   ')

        if bit == 31:
            bit = 0
            word = word + 1
        else:
            bit = bit + 1
    
    return output


def genFaults(cylinders, fault_tag, word_start, bit_start):
    """
    Generates rungs containing faults for a list of cylinder tags in L5K format with
    the ability to specify what starting word and bit to begin at. The returned string
    is copied to the clipboard for pasting into your program.

    Args:
        cylinder: A list of the cylinder tag names you want faults for.
        fault_tag: The fault tag name (ex: Sta100_Faults).
        word_start: The fault tag array index you want to start generating from.
        bit_start: The starting bit you want the faults generated from.

    Returns:
        A string in the L5K format with the rungs containing your faults.
    """

    output = ''

    cylinder_faults = ['NotAdvancingFault',
                       'NotReturningFault', 'BothSensorsOnFault']

    bit = int(bit_start)
    word = int(word_start)

    for cylinder in cylinders:
        for cylinder_fault_number in range(0, len(cylinder_faults)):
            fault = cylinder_faults[cylinder_fault_number]
            output = (
                f'{output}XIC({cylinder}.{fault})OTL({fault_tag}[{word}].{bit});   ')

            if bit == 31:
                bit = 0
                word = word + 1
            else:
                bit = bit + 1

    return output


def l5xFaultsGen(cylinders, fault_tag, word_start, bit_start):
    """
    Generates an list of strings containing a rung to import into a PLC program in
    L5X format. Used as a helper function to create a complete L5X file to import.

    Args:
        cylinder: A list of the cylinder tag names you want faults for.
        fault_tag: The fault tag name (ex: Sta100_Faults).
        word_start: The fault tag array index you want to start generating from.
        bit_start: The starting bit you want the faults generated from.

    Returns:
        A list of strings in the L5X format with the rungs containing your faults.
    """
    output = []

    cylinder_faults = ['NotAdvancingFault',
                       'NotReturningFault', 'BothSensorsOnFault']

    total_cylinders = len(cylinders)

    bit = int(bit_start)
    word = int(word_start)

    faults_per_cylinder = 3

    total_cylinder_faults = total_cylinders * faults_per_cylinder

    for cylinder in cylinders:
        for cylinder_fault_number in range(0, len(cylinder_faults)):
            output.append(
                f'XIC({cylinder}.{cylinder_faults[cylinder_fault_number]})OTL({fault_tag}[{word}].{bit})')

            if bit == 31:
                bit = 0
                word = word + 1
            else:
                bit = bit + 1

    return output


def genControlCopyPaste(cylinders, station_prefix):
    """
    Generates the control routine logic to paste into a PLC program in L5K
    format. It also copies the generated logic onto your clipboard.

    Args:
        cylinder: A list of the cylinder tag names you want faults for.
        station_prefix: The station designation (ex: Sta100, OP200, Stn1, etc.)

    Returns:
        A string in L5K format to paste into your program.
    """
    output = ''

    total_cylinders = len(cylinders)

    for cylinder in cylinders:
        output = (
            f'{output}XIC({station_prefix}_Mode.Ready)OTE({station_prefix}_{cylinder}.WorkClear);   ')
        output = (f'{output}[[XIC({station_prefix}_Mode.InCycle),XIC({station_prefix}_Mode.InStep)]NEQ({station_prefix}_{cylinder}.WorkAutoCalls,0),XIC({station_prefix}_Mode.InManual)XIC({station_prefix}_{cylinder}.WorkPB)]XIC({station_prefix}_{cylinder}.WorkClear)OTE({station_prefix}_{cylinder}.WorkReq);   ')
        output = (f'{output}[XIC({station_prefix}_{cylinder}.WorkReq),XIC({station_prefix}_{cylinder}.WorkCmd)XIC({station_prefix}_{cylinder}.WordSW)]XIO({station_prefix}_{cylinder}.HomeReq)[OTE({station_prefix}_{cylinder}.WorkCmd),XIO({station_prefix}_{cylinder}.AtWork)TON({station_prefix}_{cylinder}.MovingToWork,0,0)];   ')
        output = (
            f'{output}XIC({station_prefix}_{cylinder}.WorkSW)[TON({station_prefix}_{cylinder}.AtWorkDebounce,0,0),XIC({station_prefix}_{cylinder}.AtWorkDebounce.DN)OTE({station_prefix}_{cylinder}.AtWork)];   ')

        output = (
            f'{output}XIC({station_prefix}_Mode.Ready)OTE({station_prefix}_{cylinder}.HomeClear);   ')
        output = (f'{output}[[XIC({station_prefix}_Mode.InCycle),XIC({station_prefix}_Mode.InStep)]NEQ({station_prefix}_{cylinder}.HomeAutoCalls,0),XIC({station_prefix}_Mode.InManual)[XIC({station_prefix}_{cylinder}.HomePB),XIC({station_prefix}_Mode.HomeCmd)]]XIC({station_prefix}_{cylinder}.HomeClear)OTE({station_prefix}_{cylinder}.HomeReq);   ')
        output = (f'{output}[XIC({station_prefix}_{cylinder}.HomeReq),XIC({station_prefix}_{cylinder}.HomeCmd)XIC({station_prefix}_{cylinder}.WordSW)]XIO({station_prefix}_{cylinder}.HomeReq)[OTE({station_prefix}_{cylinder}.HomeCmd),XIO({station_prefix}_{cylinder}.AtHome)TON({station_prefix}_{cylinder}.MovingToHome,0,0)];   ')
        output = (
            f'{output}XIC({station_prefix}_{cylinder}.HomeSW)[TON({station_prefix}_{cylinder}.AtHomeDebounce,0,0),XIC({station_prefix}_{cylinder}.AtHomeDebounce.DN)OTE({station_prefix}_{cylinder}.AtHome)];   ')

        output = (
            f'{output}XIC({station_prefix}_{cylinder}.MovingToWork.DN)OTE({station_prefix}_{cylinder}.NotAdvancingFault);   ')
        output = (
            f'{output}XIC({station_prefix}_{cylinder}.MovingToHome.DN)OTE({station_prefix}_{cylinder}.NotReturningFault);   ')
        output = (
            f'{output}XIC({station_prefix}_{cylinder}.AtHome)XIC({station_prefix}_{cylinder}.AtWork)[TON({station_prefix}_{cylinder}.BothSensorsOnTimer,0,0),XIC({station_prefix}_{cylinder}.BothSensorsOnTimer.DN)OTE({station_prefix}_{cylinder}.BothSensorsOnFault)];   ')


    return output


def l5xControlGen(cylinders, station_prefix):
    """
    Generates an list of strings to import into a PLC program in L5X format.
    Used as a helper function to create a complete L5X file to import.

    Args:
        cylinder: A list of the cylinder tag names you want faults for.
        station_prefix: The station designation (ex: Sta100, OP200, Stn1, etc.)

    Returns:
        A list of strings in the L5X format with the rungs containing your cylinder control logic.
    """
    total_cylinders = len(cylinders[0])

    output = {}

    logic = []
    comments = []

    for i in range(0, len(cylinders[0])):
        cylinder = cylinders[0][i]
        name = cylinders[1][i].lstrip()
        desc1 = cylinders[2][i].lstrip()
        desc2 = cylinders[3][i].lstrip()
        station = cylinders[4][i].lstrip()

        if desc1 == '' and desc2 != '':
            comments.append(
                f'************************************************\n{station}\n{desc2}\n{name}\n************************************************\n\nWork Control\n\n')
        elif desc1 == '' and desc2 == '':
            comments.append(
                f'************************************************\n{station}\n{name}\n************************************************\n\nWork Control\n\n')
        else:
            comments.append(
                f'************************************************\n{station}\n{desc1}\n{desc2}\n{name}\n************************************************\n\nWork Control\n\n')

        logic.append(
            f'XIC({station_prefix}_Mode.Ready)OTE({cylinder}.WorkClear)')
        comments.append('')
        logic.append(f'[[XIC({station_prefix}_Mode.InCycle),XIC({station_prefix}_Mode.InStep)]NEQ({cylinder}.WorkAutoCalls,0),XIC({station_prefix}_Mode.InManual)XIC({cylinder}.WorkPB)]XIC({cylinder}.WorkClear)OTE({cylinder}.WorkReq)')
        comments.append('')
        logic.append(f'[XIC({cylinder}.WorkReq),XIC({cylinder}.WorkCmd)XIC({cylinder}.WordSW)]XIO({cylinder}.HomeReq)[OTE({cylinder}.WorkCmd),XIO({cylinder}.AtWork)TON({cylinder}.MovingToWork,0,0)]')
        comments.append('')
        logic.append(
            f'XIC({cylinder}.WorkSW)[TON({cylinder}.AtWorkDebounce,0,0),XIC({cylinder}.AtWorkDebounce.DN)OTE({cylinder}.AtWork)]')

        comments.append(f'\nHome Control\n\n')
        logic.append(
            f'XIC({station_prefix}_Mode.Ready)OTE({cylinder}.HomeClear)')
        comments.append('')
        logic.append(f'[[XIC({station_prefix}_Mode.InCycle),XIC({station_prefix}_Mode.InStep)]NEQ({cylinder}.HomeAutoCalls,0),XIC({station_prefix}_Mode.InManual)[XIC({cylinder}.HomePB),XIC({station_prefix}_Mode.HomeCmd)]]XIC({cylinder}.HomeClear)OTE({cylinder}.HomeReq)')
        comments.append('')
        logic.append(f'[XIC({cylinder}.HomeReq),XIC({cylinder}.HomeCmd)XIC({cylinder}.WordSW)]XIO({cylinder}.HomeReq)[OTE({cylinder}.HomeCmd),XIO({cylinder}.AtHome)TON({cylinder}.MovingToHome,0,0)]')
        comments.append('')
        logic.append(
            f'XIC({cylinder}.HomeSW)[TON({cylinder}.AtHomeDebounce,0,0),XIC({cylinder}.AtHomeDebounce.DN)OTE({cylinder}.AtHome)]')

        comments.append(f'\nFaults\n\n')
        logic.append(
            f'XIC({cylinder}.MovingToWork.DN)OTE({cylinder}.NotAdvancingFault)')
        comments.append('')
        logic.append(
            f'XIC({cylinder}.MovingToHome.DN)OTE({cylinder}.NotReturningFault)')
        comments.append('')
        logic.append(
            f'XIC({cylinder}.AtHome)XIC({cylinder}.AtWork)[TON({cylinder}.BothSensorsOnTimer,0,0),XIC({cylinder}.BothSensorsOnTimer.DN)OTE({cylinder}.BothSensorsOnFault)]')

    output['logic'] = logic
    output['comments'] = comments

    return output


def l5xGen(rung_logic, rung_comments):
    """
    Creates an importable L5X file to import logic into your PLC program. Includes the nessesary headers
    and footers to allow a clean import.

    Args:
        rung_logic: a list of L5X formatted strings containg logic for a rung.
        rung_comments: a list of comments for L5X formatted rungs.

    Returns:
        A completed string containing logic in L5X format to import into a PLC.
    """
    output = l5xGenHeader()

    for logic, comment in zip(rung_logic, rung_comments):

        if comment == '':
            output = f'{output}{l5xGenRung(logic)}'
        else:
            output = f'{output}{l5xGenRung(logic, comment=comment)}'

    output = f'{output}{l5xGenFooter()}'

    return output


def l5xGenRung(logic, **kwargs):
    """
    Generates L5X rungs with or without comments.

    Args:
        logic: A string containing the formatted L5X logic for a rung.
        comments (optional): A string with the text for a rung comment.

    Returns:
        A string containg properly formatted L5X text to use when generating an
        L5X import file
    """
    has_comment = False

    rung_string = ''

    # get optional comment
    if 'comment' in kwargs:
        comment = kwargs.get('comment')
        has_comment = True

    rung_comment_header = '<Comment><![CDATA['
    rung_comment_footer = ']]></Comment>'

    rung_header = '<Rung>'

    rung_data_header = '<Text><![CDATA['
    rung_data_footer = ';]]></Text></Rung>'

    if has_comment:
        rung_string = f'{rung_header}{rung_comment_header}{comment}{rung_comment_footer}{rung_data_header}{logic}{rung_data_footer}'
    else:
        rung_string = f'{rung_header}{rung_data_header}{logic}{rung_data_footer}'

    return rung_string


def l5xGenHeader():
    """
    A function to return the L5X header string.

    Args:
        None

    Returns:
        The L5X header string.
    """
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="00" TargetType="Rung" TargetCount="9" ContainsContext="true"><Controller Use="Context"><Programs Use="Context"><Program Use="Context"><Routines Use="Context"><Routine Use="Context"><RLLContent Use="Context">'

# returns the required footer for an L5X file needed on all imports


def l5xGenFooter():
    """
    A function to return the L5X footer string.

    Args:
        None

    Returns:
        The L5X footer string.
    """
    return '</RLLContent></Routine></Routines></Program></Programs></Controller></RSLogix5000Content>'

if __name__ == "__main__":
    test_parent_tags = ['Sta100_Cyl1', 'Sta100_Cyl2', 'Sta100_Cyl3']
    test_child_tags = ['WorkCmd', 'HomeCmd']
    test_fault_tag = 'Sta100_Faults'
    test_word_start = 0
    test_bit_start = 0

    test_faults = faultGen(test_parent_tags, test_fault_tag, test_word_start, test_bit_start, test_child_tags)

    print(test_faults)

    # test without child tags
    test_faults = faultGen(test_parent_tags, test_fault_tag, test_word_start, test_bit_start)

    print(test_faults)

    exit()