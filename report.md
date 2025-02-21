# Report for assignment 3

This project is an experiment in complexity and coverage metrics, based on [Discord bot](https://github.com/python-discord/bot). The goals are to get an understanding and appreciation of the benefits and drawbacks of metrics and their tools, and to create new test cases or to enhance existing tests that improve statement or branch coverage.

## Onboarding experience (Shangxuan Tang)
1. I don't have to install many additional tools to build the software except Poetry.
2. Poetry is a widely-used Python packaging and dependency management tool, well documented on the official website.
3. Other components are installed automatically by the Poetry commands.
4. The build concludes automatically without errors.
5. After setting up a Discord test server and bot account, configuring the bot, examples and tests run well on my system (Ubuntu 22.04).

We finally decide to continue on Discord bot.


## Onboarding experience (Zubair Yousafzai)
The project was easy to build and get up and running with. After cloning the repo one must just install Poetry which takes care of all dependencies needed to run the bot.
1. No additional tools needed to build the software.
2. Poetry is well documented on their official website.
3. All other components were installed using Poetry commands.
4. The build concluded without errors. There were some warnings but nothing that made the software crash.
5. The documentation helps one setup a test server as well as a bot. After doing that everything ran properly on my system (Ubuntu 24.04).

We decided on sticking with the discord bot project.

## Complexity

### on_command_error() (Shangxuan Tang)

Function: `on_command_error@65-149@./bot/exts/backend/error_handler.py`

1. The CC is 20. Everyone gets the same result and nothing is unclear. The result given by Lizard is also 20, same as ours.  
2. This function is with 76 NLOCs and CC of 20. It is both complex and long.  
3. This function is used to handle the errors. There are lots of `if` statements to get the type of the error and handle the possible exception, which is tightly related to the high CC.  
4. Exceptions in Python are taken into account by Lizard. The CC is counted 1 more time for each except block.  
5. The documentation of the function is pretty clear as comments, but it does not cover all the branches in the function (Some of these branches are self-explained by function and variable names).

### actions_for() (Zubair Yousafzai) 

Function: `actions_for64-118@bot/exts/filtering/_filter_lists/extension.py`

1. The CC of the function is 25. We used Lizard on `actions_for` and manually counted the same result.
2. The function is not only complex but also long with an NLOC of 42.
3. The function’s purpose is to filter message attachments based on allowed or disallowed file extensions, and to set the appropriate “embed description” or actions if files are blocked.  
4. Exceptions are taken into account, partly by Lizard but also by us when counting manually.
5. The documentation is clear about the general filtering process, but some branches (like special handling for `.py` or text-like files in Snekbox mode) can be inferred only by reading the code.

## deactivate_infraction() (Anton Yderberg)

Function: `deactivate_infraction() .bot/exts/moderation/infraction/_schedueler.py`

1. CC is 17. Got one partner to colaborate and Lizard gives the same result.
2. NLOC is 114 so it is also long
3. To remove an "infraction" a mark on their "record" on the discord server, and to notify all parts relevant depending on logs set. 
The main reason for its length and complexity is that it interacts with a database and needs
4. Yes +1 for every except block
5. Yes

## Refactoring

### on_command_error() (Shangxuan Tang)

The code to handle command_not_found error and command_invoke_error are complex, so I extract two methods from these two code snippets. The reduction of CC is obvious, and these functions become easier to test. There is a recursive call in original function when handling command_not_found error. The refactor makes it more maintainable, and there is no drawback.

CC before:
```shell
# NLOC    CCN   token  PARAM  length  location
    76     20     412      3      85  on_command_error@65-149@bot/exts/backend/error_handler.py
```

CC after:
```shell
# NLOC    CCN   token  PARAM  length  location
    54     12    249      3      60   on_command_error@65-124@bot/exts/backend/error_handler.py
    14      5     90      2      16   handle_command_not_found@126-141@bot/exts/backend/error_handler.py
    14      6    122      3      14   handle_command_invoke_error@143-156@bot/exts/backend/error_handler.py
```

The CC of on_command_error is reduced by 40%.

The refactored code is in branch [refactor/12-on-command-error](https://github.com/SEF-Group-25/discord-bot/compare/refactor/12-on-command-error). Check the change using:
```shell
% git diff 60905d8 61e9ca3
```

### actions_for() (Zubair Yousafzai)

- For `actions_for`, we can separate out logic related to `.py` extensions, text-like files, and Snekbox into smaller helper functions.  
- This would reduce nested `if` statements and improve readability, likely lowering the cyclomatic complexity from 25 closer to (estimated) 15–18.  
- Potential drawbacks include needing more function calls and possibly introducing multiple return points.

CC before:
```shell
# NLOC    CCN   token  PARAM  length  location  
------------------------------------------------
       4      1     35      2       4 __init__@50-53@bot/exts/filtering/_filter_lists/extension.py
       3      1     17      2       3 get_filter_type@55-57@bot/exts/filtering/_filter_lists/extension.py
       3      1     18      1       3 filter_types@60-62@bot/exts/filtering/_filter_lists/extension.py
      42     25    422      2      55 actions_for@64-118@bot/exts/filtering/_filter_lists/extension.py
```

CC after:
```shell
# NLOC    CCN   token  PARAM  length  location  
------------------------------------------------
       4      1     35      2       4 __init__@50-53@bot/exts/filtering/_filter_lists/extension.py
       3      1     17      2       3 get_filter_type@55-57@bot/exts/filtering/_filter_lists/extension.py
       3      1     18      1       3 filter_types@60-62@bot/exts/filtering/_filter_lists/extension.py
      20      9    210      2      25 actions_for@64-88@bot/exts/filtering/_filter_lists/extension.py
       3      2     48      2       3 _get_all_extensions@90-92@bot/exts/filtering/_filter_lists/extension.py
      10      5     96      3      10 _get_triggered_filters_and_allowed_ext@94-103@bot/exts/filtering/_filter_lists/extension.py
       8      6     87      4       8 _compute_not_allowed_extensions@105-112@bot/exts/filtering/_filter_lists/extension.py
      17      7    139      3      17 _set_dm_embed@114-130@bot/exts/filtering/_filter_lists/extension.py
```

The CC of actions_for is reduced from 25 to 9, a reduction of **64%**.

The refactored code is in branch [refactor/18-refactor-actions-for](https://github.com/SEF-Group-25/discord-bot/tree/refactor/18-refactor-actions-for). Check the change using:
```shell
% git diff 60905d8 c0054be
```
## deactivate_infraction() (Anton Yderberg)
Refactoring the code should be very easy, the function is grouped into 4 major tasks. The majority of the complexity comes from the try/except blocks with multiple excepts and if statements in except block. Spliting these tasks and try/except blocks will drastically reduce CC.

The final CC would be 8 (more than 35% less than the original 17)
The refactored code is in branch [refactor/15-deac-inf](https://github.com/SEF-Group-25/discord-bot/tree/origin/refactor/15-refactor-deac-inf)
This will call alot more helper function as the obvious drawback

git diff 057ccfea 60905d84

**Carried out refactoring (optional, P+):**

## Coverage

### Tools

Discord bot is already integrated with coverage tool `Coverage.py`, and the commands to use it are well documented in `./tests/README.md`. So we don't need to use `Coverage.py` directly. Discord bot uses Pytest to execute test cases, and `Coverage.py` is compatible with Pytest. So it is easy to integrate it with the build environment.

### Own coverage tool

Branch [feat/1-cov-error-handler](https://github.com/SEF-Group-25/discord-bot/tree/feat/1-cov-error-handler) shows the instrumented code. Check the code and usage of tool using:
```shell
% git diff 60905d8 cd2f974
```
### Evaluation

We use a function mark_branch(branch_id) to instrument. When the branch is reached, it will write branch id to a log file. Then we can deal with log file, count which branch ids do not appear and compute the coverage rate.

Our tool only supports branches that can be added a function call at the beginning. If without refactor of source code, the tool can't support branches like:
```python
# several conditions in if, we can't instrument for conditions seperately
if isinstance(e, errors.CommandNotFound) and not getattr(ctx, "invoked_from_error_handler", False):

# can't insert instrumentation in this line
filter_ for filter_ in self[ListType.ALLOW].filters.values() if await filter_.triggered_on(new_ctx)
```

After excluding special cases or refactoring code, the result of our tool is accurate, consistent with the result of `Coverage.py`.

## Coverage improvement (Shangxuan Tang)

### on_command_error()

Requirements documentation for uncovered branches:

```python
if await self.try_run_fixed_codeblock(ctx):
    return  # if the command body is within triple backticks, then try to invoke it
    
except Exception as err:    # error raised by those three functions in try block
    
if isinstance(err, errors.CommandError):    
    # if the error is a CommandError, use on_command_error itself to handle it
    await self.on_command_error(ctx, err)
    
else:   # else it is a invoke error
    await self.on_command_error(ctx, errors.CommandInvokeError(err))
    
elif isinstance(e.original, Forbidden):
    # handle_forbidden_from_block() handles ``discord.Forbidden`` 90001 errors, 

except Forbidden:
    # re-handle the error if it isn't a 90001 error.
    await self.handle_unexpected_error(ctx, e.original)
```

Report of old coverage:
```shell
# Name                              Stmts   Miss Branch BrPart  Cover
bot/exts/backend/error_handler.py     245     68     96      7    73%
# Missing
25-29, 33-42, 47, 109, 111-116, 134-137, 162-163, 206-207, 212, 218-220, 236-257, 265-266, 268-288, 331-339
```

Report of new coverage:
```shell
# Name                              Stmts   Miss Branch BrPart  Cover
bot/exts/backend/error_handler.py     245     58     96      5    77%
# Missing
25-29, 33-42, 47, 165-166, 209-210, 215, 221-223, 239-260, 268-269, 271-291, 334-342
```
There are 4 new test cases in branch [test/2-new-tests-error-handler](https://github.com/SEF-Group-25/discord-bot/tree/test/2-new-tests-error-handler). Check the test cases using:
```shell
% git diff 60905d8 f4ba935
```

## Coverage improvement (Zubair Yousafzai)
Below are some requirement comments for uncovered code paths in `actions_for()` that I identified:

```python
# Requirement 1: Disallow .py files with a special embed
# Requirement 2: Disallow text-like files with a different embed
# Requirement 3: SNEKBOX event should skip blocking text-like files
# Requirement 4: Return early if ctx.message is None
```

Report of old coverage:
```shell
# Name
bot/exts/filtering/_filter_lists/extension.py  

Stmts   Miss Branch BrPart  Cover
56      6     18      6    84%

# Missing
15, 62, 74, 90, 96->115, 99, 102
```

Report of new coverage:
```shell
# Name
bot/exts/filtering/_filter_lists/extension.py  

Stmts   Miss Branch BrPart  Cover
56      3     18      3    92%

# Missing
15, 62, 74, 96->115
```

There are 4 new test cases in branch [feat/6-testing](https://github.com/SEF-Group-25/discord-bot/tree/feat/6-testing). Check the test cases using:


```shell
% git diff 60905d8 8f0c188
```

## Coverage improvement (Anton Yderberg)


Requierments:
1. Call _pardon_action
2. Raise ValueError if _pardon_action returns None
3. Handle discord.Forbidden exceptions
4. Handle discord.HTTPException for 404 or code 10007
5. Record a “Failure” in the log for other HTTP exceptions
6. Check watch status of the user
7. Mark the infraction as inactive in the database
8. Append the pardon reason if provided
9. Cancel the scheduled expiration task
10. Send a mod log entry if send_log is True
11. Return a log dictionary summarizing the outcome


Report of old coverage: Branch [feat/13-cov-deac-inf](https://github.com/SEF-Group-25/discord-bot/tree/origin/feat/13-cov-deac-inf)
```shell
# Name                              Stmts   Miss Branch BrPart  Cover
bot/exts/backend/error_handler.py     248    209     68      0    12%
# Missing (relevant)
416-532, 546, 555-556 
```

Report of new coverage: Branch [feat/14-test-deac-inf](https://github.com/SEF-Group-25/discord-bot/tree/origin/feat/14-test-deac-inf)
```shell
# Name                              Stmts   Miss Branch BrPart  Cover
bot/exts/backend/error_handler.py     277    184     74      6    29%
# Missing (relevant)
469-472, 489-490, 494-497, 505->515, 509->513, 519-531, 534->539, 540-562, 587, 596-597
```

There are 4 testcases added in [feat/14-test-deac-inf](https://github.com/SEF-Group-25/discord-bot/tree/origin/feat/14-test-deac-inf)

```shell
git diff 9b2c5620 60905d84
```

## Self-assessment: Way of working

The current state is In Place according to the Essence standard. We can proficiently use git commit messages, GitHub issues to manage our code. We use different branches according to the issues to development. These practises and tools are being used by the whole team, although the requirements of different assignments vary greatly. And we get adapted to this way-of-working and benefit from it.

It still takes time to achieve Working well state, because the demand is always changing between assignments, we still need time to combine the the way-of-working and reality.

## Overall experience (Shangxuan Tang)

I learned a lot of skills and knowledge of testing, and I become more sensitive to bad smells in code. When developing softwares in the future, I will think more about how to make my code easier to test and more maintainable. This project also inspired me a lot on test driven development.

## Overall experience (Zubair Yousafzai)
My main take-away is that metrics like cyclomatic complexity and coverage can pinpoint areas needing attention, whether that’s refactoring overly complex functions or adding tests for under-tested code branches. Also I've learned that when a function is long it usually is overlooked in testing. So maybe the best way to code is to keep functions as small as possible to improve general reliability.

## Overal experience (Anton Yderberg)
My main take away from this has been the experience of interacting with and onboarding onto a well documented open source program can be very impresive (And sometimes a pain in the ass). Its interesting to see how problematic code, even when it at face value seems very proffesional, can be and the use of tools that detect cyclomatic complexity and coverage are very usefull to detect potential problem code.

## Contributions

| Group member     | Function name          | Function Location                                     |
| ---------------- | ---------------------- | ----------------------------------------------------- |
| Oscar Hellgren   |                        |                                                       |
| Anton Yderberg   | deactivate_infraction()| 393-532@bot/exts/moderation/infraction/_schedueler.py |
| Zubair Yousafzai | actions_for()          | 64-118@bot/exts/filtering/_filter_lists/extension.py  |
| Shangxuan Tang   | on_command_error()     | 65-149@./bot/exts/backend/error_handler.py            |
