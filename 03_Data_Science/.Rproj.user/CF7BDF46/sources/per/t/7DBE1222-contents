library(tidyverse)
library(lubridate)


# Read first test data
data <- read_delim(file = "data_raw/1218_2_game_data.csv", delim = ";", locale=locale(decimal_mark = ","))

# Change time format of time_stamp according to lubridate format
data$time_stamp <- dmy_hms(data$time_stamp)

# Sort data according to player_id and time_stamp to arrange data according to chronological decisiion making
data <- arrange(data, player_id, time_stamp)


# Create unique identifier for each decision made by all players
counter <- 1
data$temp <- 1

for(i in 1:nrow(data)){
  tryCatch( {
    condition <- data$decision_count[i] == data$decision_count[i-1]
    if (condition) {
      data$temp[i] <- counter
    } else {
      counter <- counter + 1
      data$temp[i] <- counter
    }
  },
  error = function(exception) {
    print('end of file reached')
  },
  finally = {
    data$temp[i] <- counter

  }

  )


}

### Identify all decisions that led to a goal for team 1 and 2
data <- data %>% mutate(action1 = if_else(goal_team_1 < lead(goal_team_1), temp, 0),
                        action2 = if_else(goal_team_2 < lead(goal_team_2), temp, 0))
data <- data %>% mutate(goal_action_1 = if_else(temp %in% subset(data$action1, data$action1 != 0), temp, 0))
data <- data %>% mutate(goal_action_2 = if_else(temp %in% subset(data$action2, data$action2 != 0), temp, 0))


### Goal label created (5; -5)
data <- data %>% mutate(label = if_else((team_id == 1 & goal_action_1 != 0) | (team_id == 2 & goal_action_2 != 0), 5, 0),
                        label = if_else((team_id == 1 & goal_action_2 != 0) | (team_id == 2 & goal_action_1 != 0), -5, label))

# Use second last action for attacker
temps <- data %>% filter(label == 5) %>% .$temp %>% unique() - 1
data <- data %>% mutate(label = if_else(label == 5, 0, label),
                label = if_else(temp %in% temps, 5, label))

### Score for guard (-0.25; 0.25)
value <- 0.25
data <- data %>% mutate(label = if_else(label != -5 & decision == 'guard', label + value, label),
                        label = if_else(label == -5 & decision == 'guard', label - value, label))


### Score for center (-0.25; 0.25) -> Create new column for center line
value <- 0.25
data <- data %>% mutate(center_line = (goal_1_post_1_x + goal_1_post_2_x + goal_2_post_1_x + goal_2_post_2_x) / 4)
data <- data %>% mutate(center_temp = if_else(temp < lead(temp) & decision == 'center', 1, 0),
                        label = if_else(center_temp == 1 & ((team_id == 1 & ball_x < center_line) | (team_id == 2 & ball_x > center_line)), label + value, label))

temps <- data %>% filter(decision == 'center' & label != 0) %>% select(label, temp)
for (i in 1:nrow(temps)){
  data <- data %>% mutate(label = if_else(temp == temps[[i,2]], temps[[i,1]], label))
}


### Score for shoot, intercept, recover [1, -1]
# Create goal coordinates
data <- data %>% mutate(goal_1_x = mean(c(goal_1_post_1_x, goal_1_post_2_x)),
                        goal_1_y = mean(c(goal_1_post_1_y, goal_1_post_2_y)),
                        goal_2_x = mean(c(goal_2_post_1_x, goal_2_post_2_x)),
                        goal_2_y = mean(c(goal_2_post_1_y, goal_2_post_2_y)),
                        separator = 0)

# Create new time variable (rounded down using floor())
data <- data %>% mutate(floor_time = floor(time))
temp_sizes <- data %>% group_by(temp) %>% tally()
data <- data %>% mutate(
       separator = if_else(temp < lead(temp) | is.na(lead(temp)), 2, separator),
       separator = if_else(lag(temp) < temp | is.na(lag(temp)), 1, 0),
       dist_goal_1_sep_1 = if_else(separator == 1, sqrt((goal_1_x - ball_x)^2 + (goal_1_y - ball_y)^2), 0),
       dist_goal_2_sep_1 = if_else(separator == 1, sqrt((goal_2_x - ball_x)^2 + (goal_2_y - ball_y)^2), 0),
       dist_goal_1_sep_2 = 0,
       dist_goal_2_sep_2 = 0,
       lead_to_sep_2 = 0)

for (i in 1:nrow(temp_sizes)){
  data <- data %>% mutate(lead_to_sep_2 = if_else(separator == 1 & temp == temp_sizes[[i,1]], temp_sizes[[i,2]] - 1, lead_to_sep_2))
}

seps <- data %>% mutate(ii = 1:nrow(data)) %>% filter(separator == 1) %>% select(temp, lead_to_sep_2, ii, player_id)
is.na(seps[288,1]$temp)
# Create columns to check ball improvement
max_lead <- 4
for (i in 1:nrow(seps)){
  lead_num <- NA
  for (j in max_lead:1){
    if (!is.na(lead_num)){
      lead_num <- if_else(is.na(data[seps[[i,3]] + seps[[i,2]] + j]$player_id) | data[seps[[i,3]]]$player_id != data[seps[[i,3]] + seps[[i,2]] + j]$player_id, NA, j)
    }
  }
  if (is.na(lead_num)){
    lead_num = 0
  }
  data <- data %>% mutate(
    dist_goal_1_sep_2 = if_else(separator == 1 & temp == seps[[i,1]], sqrt((lead(goal_1_x, seps[[i,2]] + lead_num) - lead(ball_x, seps[[i,2]] + lead_num))^2 + (lead(goal_1_y, seps[[i,2]] + lead_num) - lead(ball_y, seps[[i,2]] + lead_num))^2), dist_goal_1_sep_2),
    dist_goal_2_sep_2 = if_else(separator == 1 & temp == seps[[i,1]], sqrt((lead(goal_2_x, seps[[i,2]] + lead_num) - lead(ball_x, seps[[i,2]] + lead_num))^2 + (lead(goal_2_y, seps[[i,2]] + lead_num) - lead(ball_y, seps[[i,2]] + lead_num))^2), dist_goal_2_sep_2),
    )

}

data <- data %>% mutate(
  my_goal_distance_1 = if_else(team_id == 1, dist_goal_1_sep_1, dist_goal_2_sep_1),
  my_goal_distance_2 = if_else(team_id == 1, dist_goal_1_sep_2, dist_goal_2_sep_2),
  opp_goal_distance_1 = if_else(team_id == 1, dist_goal_2_sep_1, dist_goal_1_sep_1),
  opp_goal_distance_2 = if_else(team_id == 1, dist_goal_2_sep_2, dist_goal_1_sep_2),
  sub_label_1 = if_else(decision %in% c('intercept', 'shoot', 'recover') & separator == 1, opp_goal_distance_1 / (opp_goal_distance_1 + my_goal_distance_1) , 0),
  sub_label_2 = if_else(decision %in% c('intercept', 'shoot', 'recover') & separator == 1, opp_goal_distance_2 /(opp_goal_distance_2 + my_goal_distance_2), 0),
  label = if_else(decision %in% c('intercept', 'shoot', 'recover') & separator == 1, if_else(sub_label_1 > sub_label_2, label + (sub_label_1 - sub_label_2) / sub_label_1, label + (sub_label_1 - sub_label_2) / (1 - sub_label_1)), label))


temps <- data %>% filter(decision %in% c('intercept', 'shoot', 'recover') & separator == 1) %>% select(label, temp)
for (i in 1:nrow(temps)){
  data <- data %>% mutate(label = if_else(temp == temps[[i,2]], temps[[i,1]], label))
}

labeled_data <- data[c(-1, -7, -(32:37), -(39:57))]
write_csv(labeled_data, 'labeled_data.csv')
