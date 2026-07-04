class general_settings():
    MAX_WATCHDOG = 5
    VERSION_SOFTWARE = "2.0"
    VERSION_PARSER = "2.0"
    VERSION_RECEIVER = "1.1"
    NAME = "Engine Plotting Software"


class data_settings():
    DEFAULT_FORMAT = "csv"
    DEFAULT_HEADER_DENOMINATOR = "#"
    DEBUG_DIRECTORY = "testing_directory"
    INVALID_CHARACTERS = r'<>:"/\|?*'
    CSV_DELIMITER = ","
    DEBUG_MODE = True
    TELEMETRY_SETTING = 1 # 1 = Partial Telemetry (RPM, points), 2 = Full Telemetry (RPM, Time, points)


    
class graphing_settings():
    # Basic settings
    GENERATE_GRAPH = True
    SAVE_FIG = False # Saves the generated graph to file
    ANIMATE = False

    # Technical settings
    MAX_WATCHDOG = 5 # maximum number of attempts for file input
            # ratio of data / stat_text, if enabled
    COLLUMN_NUMBER = 10
    GRAPH_COLLUMNS = 7
            # resolution of canvas
    SIZE_X = 22 # canvas size, width
    SIZE_Y = 10 # canvas size, height
    
    # data filter and form settings
    LIMIT_ACCELERATION = True # turns on MAX_ACCELERATION limit, if False will display all calculated values
    ACCELERATION_LOG10 = False # displays acceleration in symlog scale
    MAX_ACCELERATION = 1500 #maximum acceleration that will still be displayed, no data lost
    STAT_TEXT = True # info board with some useful and cool stats

    # Graphical settings
    TITLE_SIZE = 28
    LABEL_SIZE = 12 # basically everything not a title uses this
    AX1_COLOR = "black" # color of main (rpm) line
    AX2_COLOR = "#237fd4" # color of secondary line
    AX1_LINE = 2.5 # linewidth of the main (rpm) line
    