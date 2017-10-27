import argparse
from validator import EmailsFile, EmailValidator


if __name__ == "__main__":
    # Parser
    parser = argparse.ArgumentParser(description='Process and validate emails.')
    parser.add_argument('path', metavar='p', type=str, help='Path to csv file')

    args = parser.parse_args()

    email_file = EmailsFile(args.path)

    for emails in email_file.emails:
        validator = EmailValidator(emails, emails[0].get_domain())
        validator.validate_all()
        email_file.refresh()
