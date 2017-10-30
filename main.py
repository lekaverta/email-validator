import argparse
from validator import EmailsFile, EmailValidator


if __name__ == "__main__":
    # Parser
    parser = argparse.ArgumentParser(description='Process and validate emails.')
    parser.add_argument('path', metavar='p', type=str, help='Path to csv file')
    parser.add_argument('email_column', metavar='c', type=str, help='Email column description')

    args = parser.parse_args()

    email_file = EmailsFile(args.path, args.email_column)

    for emails in email_file.emails:
        validator = EmailValidator(emails, emails[0].get_domain())
        validator.validate_all()
        email_file.refresh()
