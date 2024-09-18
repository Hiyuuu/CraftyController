#!/bin/bash

# Ensure locale is set to C for predictable sorting
export LC_ALL=C
export LC_COLLATE=C
# Get current master branch supported linux versions
data=$(curl -s "https://gitlab.com/crafty-controller/crafty-installer-4.0/-/raw/refactor/versions/linux_versions.json?ref_type=heads")

# Save the JSON data to a file
echo "$data" > data.json

# Transform JSON into a format that Mustache can handle dynamically
jq -n --argjson data "$data" '
  {
    distributions: [
      $data | to_entries[] | 
      {
        name: .key,
        versions: (
          if (.value.versions | length == 0) 
          then "Rolling Release" 
          else (.value.versions | join(", ")) 
          end
        ),
        support_level: .value["support-level"]
      }
    ]
  }' > formatted_data.json

# Render the template using mustache
mustache formatted_data.json templates/table.mustache > output.md

echo "Template rendered to output.md"