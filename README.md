# Gmail Cleanser

Based on Gmail labels, this python script will tag emails in Gmail as `Trash` for eventual deletion

## Description

The script will take a list of labels (global `LABEL`), and find all sub-labels associated with it. Once all labels are found, it will put those labels into a Gmail search term (including `older_than:`), get all messages that satisfy the search and will put them in the Trash folder where Gmail will delete permanently after 30 days.

## Getting Started

Add `GMAIL_USER` and `GMAIL_PASSWORD` to a local `.env` file or as environment variables, eg:
```
GMAIL_USER=user@gmail.com
GMAIL_PASSWORD=password123
```

Add all labels you want as a part of the cleansing to the `LABEL` global list and set the `OLDER_THAN` variable. Always try testing your final search-string in Gmail to make sure it returns the results you expect.
For example, having the `Ad` label in the `LABEL` list will search for emails under the label `Ad`, and `Ad/*`.
By default, the search-string excludes any emails that are starred or marked as important. This way you can still keep emails with those labels without them being trashed.

### Dependencies

* Python 3
* python-dotenv

## Authors

Contributors names and contact info 
* [@Zaphod137](https://twitter.com/Zaphod137)

## Version History

* 0.1
    * Initial version

## Todos

* Use command line args instead of globals to build search-string
* Logging
* Option to skip trash and go straight to permanent deletion

