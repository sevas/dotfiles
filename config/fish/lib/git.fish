

set -gx ZSH_THEME_GIT_PROMPT_PREFIX " on $magenta"
set -gx ZSH_THEME_GIT_PROMPT_SUFFIX "$normal"
set -gx ZSH_THEME_GIT_PROMPT_DIRTY "$green!"
set -gx ZSH_THEME_GIT_PROMPT_UNTRACKED "$cyan?"
set -gx ZSH_THEME_GIT_PROMPT_CLEAN ""

# set -gx ZSH_THEME_GIT_PROMPT_ADDED "$yellow+"
# set -gx ZSH_THEME_GIT_PROMPT_MODIFIED "$green""M"
# set -gx ZSH_THEME_GIT_PROMPT_DELETED "$red-"
# set -gx ZSH_THEME_GIT_PROMPT_RENAMED "$yellowR"
# set -gx ZSH_THEME_GIT_PROMPT_UNMERGED "$magenta||"


# function current_branch() {
#   ref=$(git symbolic-ref HEAD 2> /dev/null) || return
#   echo ${ref#refs/heads/}
# }

# parse_git_dirty () {
#   set gitstat (git status 2>/dev/null | grep '\(# Untracked\|# Changes\|# Changed but not updated:\)')

#   if echo $gitstat | grep -c "^# Changes to be committed:$") > 0
#     echo -n "$ "
#   end

#   if [[ $(echo ${gitstat} | grep -c "^\(# Untracked files:\|# Changed but not updated:\|# Changes not staged for commit:\)$") > 0 ]]; then
#     echo -n "$ZSH_THEME_GIT_PROMPT_UNTRACKED"
#   end

#   if [[ $(echo ${gitstat} | grep -v '^$' | wc -l | tr -d ' ') == 0 ]]; then
#     echo -n "$ZSH_THEME_GIT_PROMPT_CLEAN"
#   end
# end



# Get the status of the working tree
function git_prompt_status
  set -l INDEX (git status --porcelain ^ /dev/null)
  set -l STATUS ""
  if echo "$INDEX" | grep '?? ' > /dev/null ^&1
    set STATUS "$ZSH_THEME_GIT_PROMPT_UNTRACKED$STATUS"
  end

  set is_dirty 0

  if echo "$INDEX" | grep 'A  ' > /dev/null ^&1
    set STATUS "$ZSH_THEME_GIT_PROMPT_ADDED$STATUS"
    set is_dirty 1
  else if echo "$INDEX" | grep 'M  ' > /dev/null ^&1
    set STATUS "$ZSH_THEME_GIT_PROMPT_ADDED$STATUS"
    set is_dirty 1
  end

  if echo "$INDEX" | grep ' M ' > /dev/null ^&1
    set STATUS "$ZSH_THEME_GIT_PROMPT_MODIFIED$STATUS"
    set is_dirty 1
  else
    if echo "$INDEX" | grep 'AM ' > /dev/null ^&1
      set STATUS "$ZSH_THEME_GIT_PROMPT_MODIFIED$STATUS"
      set is_dirty 1
    end
  else
    if echo "$INDEX" | grep ' T ' > /dev/null ^&1
      set STATUS "$ZSH_THEME_GIT_PROMPT_MODIFIED$STATUS"
      set is_dirty 1
    end
  end


  if echo "$INDEX" | grep 'R  '  > /dev/null ^&1
    set STATUS "$ZSH_THEME_GIT_PROMPT_RENAMED$STATUS"
    set is_dirty 1
  end

  if echo "$INDEX" | grep ' D '  > /dev/null ^&1
    set STATUS "$ZSH_THEME_GIT_PROMPT_DELETED$STATUS"
    set is_dirty 1
  else
    if echo "$INDEX" | grep 'AD '  > /dev/null ^&1
        set STATUS "$ZSH_THEME_GIT_PROMPT_DELETED$STATUS"
        set is_dirty 1
    end
  end

  if echo "$INDEX" | grep 'UU ' > /dev/null ^&1
    set STATUS "$ZSH_THEME_GIT_PROMPT_UNMERGED$STATUS"
    set is_dirty 1
  end

  if [ $is_dirty != 0 ]
    set STATUS "$ZSH_THEME_GIT_PROMPT_DIRTY$STATUS"
  end

  echo $STATUS
end
