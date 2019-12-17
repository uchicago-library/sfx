#!/exlibris/sfx_ver/sfx4_1/app/perl/bin/perl
#--------------------------------------------------------------------
# Send comments about sfx
# Reads metadata from URL and sends them to email recipient,
# but before sending asks for name, email and comments of the user
#--------------------------------------------------------------------
use strict;
use CGI;
use NetWrap::Email qw(is_valid_email);
use Output::Template;
use File::Basename;

use constant DEFAULT_EMAIL => 'your@email_address.here';

our $p = new CGI;
my $tmpldir = "$ENV{'SFXCTRL_HOME'}/templates/targets/feedback";
my $charset = 'UTF-8';

# Email used in case you dont want to set it up as a parse param
my $mail_to = '';

# otherwise we get it from the cgi input
my $mail_to ||= $p->param('em');

#In case the email was not populated yet, try to take it from config file.
if (!$mail_to) {
    use Manager::Config;
    my $config = Manager::Config->new('file'=>'ctx_object.config');
    $mail_to = $config->getSection('mix_html_menu', 'mail_to');
}

print $p->header(-charset=>$charset);

# Validate the mail_to address
if (!is_valid_email($mail_to) or ($mail_to eq DEFAULT_EMAIL))
{
     my $error_template = Output::Template->new(
		filename			=> "$tmpldir/msgerr.tmpl",
		die_on_bad_params	=> 0,
		global_vars			=> 1,
		);

    $error_template->param(ERROR => "Invalid email address: '$mail_to'."); 
    print $error_template->output;
    exit;
}

# $p->param('username') && 
# check required fields
if ($p->param('useremail') &&
    $p->param('affiliation') &&
    $p->param('usercomment'))
{
    my $mail_from = $p->param('username') . "<" . $p->param('useremail') . ">";
    my $record_title = "SFX Record Problem: ";
    # $record_title .= $p->param('bookt') if $p->param('bookt');
    $record_title .= $p->param('articlet') if $p->param('articlet');

    my $msg = '';
    $msg .= "\n\n** Sender Info **";
    $msg .= "\nName: " . $p->param('username') if $p->param('username');
    $msg .= "\nEmail: " . $p->param('useremail') if $p->param('useremail');
    $msg .= "\nAffiliation: " . $p->param('affiliation') if $p->param('affiliation');
    $msg .= "\n\n** User Comments **\n" . $p->param('usercomment') if $p->param('usercomment');
    $msg .= "\n\n** Metadata **\n";
    $msg .= "\nBook Title: " . $p->param('bookt') if $p->param('bookt');
    $msg .= "\nConference Title: " . $p->param('conft') if $p->param('conft');
    if ($p->param('author')) {
		$msg .= "\nAuthor: " . $p->param('author');
	} elsif ($p->param('aufirst')) {
		$msg .= "\nAuthor: " . $p->param('aufirst')." ".$p->param('aulast');
	}
    $msg .= "\nArticle Title: " . $p->param('articlet') if $p->param('articlet');
    $msg .= "\nJournal: " . $p->param('journal') if $p->param('journal');
    $msg .= "\nAbbreviated Journal: " . $p->param('abbrevjl') if $p->param('abbrevjl');
    $msg .= "\nVolume: " . $p->param('volume') if $p->param('volume');
    $msg .= "\nIssue: " . $p->param('issue') if $p->param('issue');
    $msg .= "\nYear: " . $p->param('year') if $p->param('year');
    $msg .= "\nPages: " . $p->param('pages') if $p->param('pages');
    $msg .= "\nISBN: " . $p->param('isbn') if $p->param('isbn');
    $msg .= "\nISSN: " . $p->param('issn') if $p->param('issn');
    $msg .= "\nSID: " . $p->param('sid') if $p->param('sid');
    $msg .= "\nOpenURL: " . $p->param('openurl') if $p->param('openurl');
   
    my %mail = (
        To				=> $mail_to,
        Cc				=> '',
        From			=> $mail_from,  
        'Reply-To'		=> $mail_from,
        Message			=> $msg,
        'Content-Type'	=> "text/plain; charset=$charset",
        Subject			=> $record_title
    );

    my $mailer = NetWrap::Email->new(%mail);

    if ($mailer->send())
	{
        my $sent_template = Output::Template->new(
                             filename =>"$tmpldir/msgsent.tmpl",
                             die_on_bad_params => 0,
                             global_vars => 1);

        print $sent_template->output;
    }
	else
	{
        my $error_template = Output::Template->new(
                                 filename =>"$tmpldir/msgerr.tmpl",
                                 die_on_bad_params => 0,
                                 global_vars => 1);


        $error_template->param(ERROR => $NetWrap::Email::error);
        print $error_template->output;
    }
}
else
{
    my $form_file = Output::Template->new(
                              filename =>"$tmpldir/feedback.tmpl",
                              die_on_bad_params => 0,
                              global_vars => 1);

    my @params = $p->param;
    my $substitute = {};
    my @fields;
    foreach my $parname (@params){
        my %vars;
        my $parval =  $p->param($parname);
        $vars{'PARNAME'} = $parname;
        $vars{'PARVALUE'} = $parval;
        push(@fields,\%vars);
    }
    $form_file->param(FIELDS=>\@fields);
	$form_file->param(ACTION=>$ENV{'SCRIPT_NAME'});
    print $form_file->output;
}

exit;
