#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(data.table)
  library(dplyr)
  library(jsonlite)
  library(openxlsx)
  library(yaml)
  library(zoo)
})

arg_value <- function(args, name, default) {
  prefix <- paste0(name, "=")
  match <- args[startsWith(args, prefix)]
  if (length(match) == 0) {
    return(default)
  }
  sub(prefix, "", match[[1]], fixed = TRUE)
}

sha256_file <- function(path) {
  output <- system2("shasum", c("-a", "256", path), stdout = TRUE)
  strsplit(output[[1]], " ")[[1]][[1]]
}

git_output <- function(repo, args) {
  system2("git", c("-C", repo, args), stdout = TRUE)
}

round_numeric_columns <- function(frame) {
  as.data.frame(lapply(frame, function(column) {
    if (is.numeric(column)) {
      column <- round(column, 6)
      column[!is.finite(column)] <- NA_real_
      return(column)
    }
    column
  }))
}

args <- commandArgs(trailingOnly = TRUE)
repo <- arg_value(
  args,
  "--repo",
  Sys.getenv(
    "TREASURY_INCOME_EXPLORER_PATH",
    unset = "/Users/maxghenis/_axiom-worktrees/nz-treasury-income-explorer"
  )
)
parameter_file <- arg_value(
  args,
  "--parameter-file",
  file.path(repo, "inst/parameters/TY27_BEFU25.yaml")
)
output_path <- arg_value(
  args,
  "--output",
  "data/oracles/treasury-emtr-snapshot.json"
)

source(file.path(repo, "R", "params_template.R"))
source(file.path(repo, "R", "util.R"))
source(file.path(repo, "R", "emtr.R"))

parameters <- parameters_from_file(parameter_file)

sample_weekly_gross_wage <- c(0, 160, 250, 370, 555, 740, 1000, 1500)
output_columns <- c(
  "gross_wage1",
  "hours1",
  "gross_wage1_annual",
  "gross_wage2",
  "wage1_tax",
  "wage1_ACC_levy",
  "net_wage1",
  "net_wage",
  "net_benefit",
  "FTC_abated",
  "IWTC_abated",
  "MFTC",
  "IETC_abated",
  "WinterEnergy",
  "BestStart_Total",
  "AS_Amount",
  "WFF_abated",
  "Net_Income",
  "Net_Income_annual",
  "EMTR",
  "RR",
  "PTR"
)

scenarios <- list(
  list(
    id = "single_parent_three_children_area1_rent",
    description = "Single parent, children aged 0, 1, and 10, Area 1 rent.",
    Partnered = FALSE,
    wage1_hourly = 18.5,
    Children_ages = c(0, 1, 10),
    gross_wage2 = 0,
    hours2 = 0,
    AS_Accommodation_Costs = 600,
    AS_Accommodation_Rent = TRUE,
    AS_Area = 1L
  ),
  list(
    id = "couple_two_children_area2_mortgage",
    description = "Couple, children aged 2 and 15, partner not working, Area 2 mortgage.",
    Partnered = TRUE,
    wage1_hourly = 18.5,
    Children_ages = c(2, 15),
    gross_wage2 = 0,
    hours2 = 0,
    AS_Accommodation_Costs = 800,
    AS_Accommodation_Rent = FALSE,
    AS_Area = 2L
  ),
  list(
    id = "couple_one_child_partner_10h_area3_rent",
    description = "Couple, child aged 9, partner working 10 hours, Area 3 rent.",
    Partnered = TRUE,
    wage1_hourly = 18.5,
    Children_ages = c(9),
    gross_wage2 = 185,
    hours2 = 10,
    AS_Accommodation_Costs = 600,
    AS_Accommodation_Rent = TRUE,
    AS_Area = 3L
  ),
  list(
    id = "single_no_children_area2_no_housing_costs",
    description = "Single adult, no children, no qualifying housing costs.",
    Partnered = FALSE,
    wage1_hourly = 18.5,
    Children_ages = c(),
    gross_wage2 = 0,
    hours2 = 0,
    AS_Accommodation_Costs = 0,
    AS_Accommodation_Rent = TRUE,
    AS_Area = 2L
  )
)

scenario_outputs <- lapply(scenarios, function(spec) {
  model_output <- emtr(
    Parameters = parameters,
    Partnered = spec$Partnered,
    wage1_hourly = spec$wage1_hourly,
    Children_ages = spec$Children_ages,
    gross_wage2 = spec$gross_wage2,
    hours2 = spec$hours2,
    AS_Accommodation_Costs = spec$AS_Accommodation_Costs,
    AS_Accommodation_Rent = spec$AS_Accommodation_Rent,
    AS_Area = spec$AS_Area,
    max_wage = max(sample_weekly_gross_wage),
    steps_per_dollar = 1L
  )

  selected <- model_output[gross_wage1 %in% sample_weekly_gross_wage, ..output_columns]
  selected <- selected[order(gross_wage1)]

  list(
    id = spec$id,
    description = spec$description,
    inputs = spec[setdiff(names(spec), c("id", "description"))],
    sampled_outputs = round_numeric_columns(selected)
  )
})

snapshot <- list(
  generated_at = as.character(Sys.Date()),
  oracle = list(
    id = "treasury-income-explorer",
    name = "NZ Treasury IncomeExplorer",
    url = "https://github.com/Treasury-Analytics-and-Insights/IncomeExplorer",
    local_path = normalizePath(repo),
    commit = git_output(repo, c("rev-parse", "HEAD"))[[1]],
    commit_date = git_output(repo, c("log", "-1", "--format=%cI"))[[1]],
    parameter_file = sub(paste0(normalizePath(repo), "/"), "", normalizePath(parameter_file)),
    parameter_file_sha256 = sha256_file(parameter_file),
    parameter_vintage = "TY27_BEFU25",
    model_year = parameters$modelyear
  ),
  generator = list(
    script = "programs/nz/generate_treasury_emtr_snapshot.R",
    treasury_function = "R/emtr.R#emtr",
    sampled_weekly_gross_wage = sample_weekly_gross_wage,
    output_columns = output_columns,
    note = "Treasury outputs are weekly unless the column name says annual."
  ),
  scenarios = scenario_outputs
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
write_json(snapshot, output_path, pretty = TRUE, auto_unbox = TRUE, digits = NA, na = "null")
cat(output_path, "\n")
