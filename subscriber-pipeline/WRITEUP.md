# Subscriber Cancellations Data Pipeline

The source database contained separate student, course, and job tables, with contact details stored as JSON and several numeric fields represented as text. I built a repeatable pipeline that parses the contact data, converts numeric values, joins the lookup tables, validates that records exist, and publishes one analytics-ready `subscribers` table plus a CSV extract.

The pipeline keeps operational concerns separate from transformation logic: unit tests protect row counts and output creation, `error.log` records failures, `changelog.log` records successful publications, and the Bash wrapper runs the complete update flow with one command.
