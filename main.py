import argparse
from validator import EmailsFile, EmailValidator


if __name__ == "__main__":
    # Parser
    parser = argparse.ArgumentParser(description='Process and validate emails.')
    parser.add_argument('path', metavar='p', type=str, help='Path to csv file')
    parser.add_argument('email_column', metavar='c', type=str, help='Email column description')
    parser.add_argument('validate_just_domain', metavar='d', type=str, help='Y if is just to validate domains')

    args = parser.parse_args()
    just_domains = False
    if (args.validate_just_domain == 'Y'):
        just_domains = True

    email_file = EmailsFile(args.path, args.email_column)

    for emails in email_file.emails:
        validator = EmailValidator(emails, emails[0].get_domain(), just_domains)
        validator.validate_all()

    print("Sanitized file: {}".format(email_file.generate_sanitized_output()))
    print("Invalids file: {}".format(email_file.generate_invalids_output()))

