#!/usr/local/bin/perl -wT

# save the entered info to a file & redisplay
# this script is intended to management info that is editable by 
# the course intructors:  course.cgi is a more general tool

$ENV{PATH} = "/bin:/usr/bin";

use Date::Calc qw { Today Delta_Days Add_Delta_Days};
use lib '/www/jobs/lib/';

use Job_Ad_MetaData;
use Job_Appl_Info3;
use Debug;
use strict;
use CGI;
use CGI::Carp 'fatalsToBrowser';

my $this_script = "/cgi-bin/Jobs/Apply";

my $title = "P &amp; A Job Form";
my $title2 = " ";
my $New = 0;	
my $version = "1.2.3";
my $tdtopright = '<td valign="top" align="right">';
my $tdtop      = '<td valign="top">';
my $styleURL = '/jobs/lib/job.css';

                      
my $wel_new = " Please enter the appropriate values";
my $wel_old = " You can edit the following info for this item:";
my $wel;
my $sp = '&nbsp;';

my %Upload_File_Prompts = ( CV_File  => "CV file",
                            Research  => "Research",
                            Pubs      => "Publications",
                            Teach     => "Teaching ",
                            other_file => "Other"
                          );
my $q = new CGI;

print $q->header(-type=> "text/html", -expires=>'now'), "\n";
print $q->start_html( -title   => "PandA Online Job Applocation Info ", 
                      -style   => {'src'=> $styleURL },
                    ),"\n";

my $offline = "/var/www/cgi-bin/Jobs/Off_Line";
if (-f $offline)      # print warning & exit
{
   my $mtime = (stat $offline)[9];
   my @time = localtime($mtime);
   my $year= 1900 + $time[5];
   my $lt = sprintf "%4d-%2.2d-%2.2dT%2.2d:%2.2d", $year, 
            $time[4], $time[3], $time[2], $time[1];
   my $TZ = $time[8] ? "PDT" : "PST";
   my $warn = "The Physics & Astronomy Job Application form is currently 
               offline either for maintenance or there are no current openings.
               Please check back in couple of hours  or contact the email
               suggested by  jobs-%%-AT-%%-phas.ubc.ca";
   print "<h2> $warn </h2>";
   print "<p> This was posted at $lt $TZ.</p>";
   print $q->end_html;
   exit;
}		    
print $q->startform("POST", $this_script,"multipart/form-data"), "\n";
   
####     Dispatch table...
####
#### Edit Button Value       Written at line# in subroutine
####  
####   action    --> confirm   do_confirm
####   goto_File --> UpLoad    do_FileUpload
####   goto_File --> Not now   do_No_CV
####   Read_File --> ???       do_Read_File
####   edit      --> Confirm   Save_params
Form_Welcome();

#print "try dumping the query edit field ",  $q->param('edit')," <br />";
#print "dump query...<br />";
#dump_it();

my $Hidden ="";
if ($q->param('action') eq "confirm")
{        
   do_confirm();       
#   do_thanks($Hidden);
} elsif ($q->param('Done')  ) 			         #
{
   do_Done();
} elsif ($q->param('goto_File') eq 'UpLoad' ) 			         #
{
   do_FileUpload();
}  elsif ($q->param('goto_File') eq 'Not now' )
{
   do_No_CV();
} elsif ($q->param('Read_File') ) 			#
{
    do_Read_File();
} elsif ($q->param('edit') eq 'Confirm')       #back 
{ 
    Save_params();
    do_thanks($Hidden);   
} elsif ($q->param('edit') eq 'Back')
{ 
    print "back Button Selected<br />";
    do_form();
} elsif ($q->param('Apply') ) 		#back from edit info page (ie cancel)
{ 
 
    do_form();
} else
{
    do_welcome_page();
#    do_form();
}

print $q->end_html;
exit;

sub do_confirm
{  
    my $joblist = $q->param(-name=>"joblist");
    my ($jtit, $jid) = split " ID : ", $q->param(-name=>"joblist");
    my $special = $q->param(-name=>"specialization");

    print "<h2>Please check this data.. </h2>\n ";
    print "<center><table>\n";
    print qq{<tr><td class="prompt">Job ID </td>\n};
    print qq{    <td class="important">$jid</td></tr>\n};
    print qq{<tr><td class="prompt">Job Title </td>\n};
    print qq{    <td  class="important">$jtit</td></tr>\n};
#    print "<tr><td><strong>Specialization:</td>";
#    print "    <td>$special</td></tr>\n";
    my %element_info = Job_Appl_Info3::get_element_info();
    foreach my $cat (  "pers", "cont",  "prof" )

    {
       foreach my $t ( sort {$element_info{$cat}{$a}{rank} <=>
                             $element_info{$cat}{$b}{rank} } 
                         keys %{ $element_info{$cat}} )
       {
           print "<tr><td><strong> $element_info{$cat}{$t}{prompt} :</strong></td>\n";
           my $out = $q->param(-name=>$t);
           $out =~ s/\(select one\)// if $t eq "citizenship";
           if ($out)
           {
               print " "x4,  "<td>$out</td></tr>\n";
           } else
           {
               print qq{    <td class="notentered">not entered</td>\n};
           }
       }
     }
     print "<tr>",
            '    <td align="left">',      $q->submit(-name=>'edit',-value=>'Confirm'),
            '    </td><td align="left">', $q->submit(-name=>'edit',-value=>'Back'),'</td></tr>',"\n";

     print "</table></center>\n";
     my $Hidden = Hide_params();
#    dump_it();

## added 2005-10-24 to address BU concerns:

     print qq{<p> By selecting <strong>"Confirm"</strong> a file will be 
                 created for this application & you will be asked if you want
                 to upload any documentation, (ie CV, Publication list, 
                 a statement of research interests, a statement  of teaching 
                 interests, or some other document). Note that it is not 
                 necessary to submit copies of research papers at this time;
                 the search committee will contact you if such documentation
                 is deemed desirable. If you choose <strong>NOT</strong> to 
                 upload some or all of the requested documentation at this 
                 time, you can submit at a latter date via email to 
                 &lt;jobs\@phas.ubc.ca&gt; <br />
              Please quote the competition number, $jid ,  in your email</p>};

     print '<p> By selecting <strong>"Back"</strong>, you will be allowed 
                   to edit the above data.';
}

sub do_form
{
    my %element_info = Job_Appl_Info3::get_element_info();
    my @curr_jobs = Get_Current_Jobs();

   my @Specs = (  "Biological Physics",
                   "Planetary Science",
                   "Theoretical Quantum Information and Computation",
                   "Theoretical Particle Physics and Cosmology",
                   "Other Specialization"
                );

#print the welcome    
        $wel = $wel_new;
        $wel = <<endxxx;
The first block of information is welcome junk<br>
endxxx

#       dump_it();

    my ($t);
    my $sp = '&nbsp;';
    my $cellpad = ' cellpadding="4" ';
  

# the editables: 
#      print " Do editables here ...<br />";
    my $v = "";
  #  my $req_flag = '<span class="required">*</span>';
    my $req = '<span class="required">*</span>';
    
    
    print "<h2>Step 1: Personal Information </h2> $req  denotes required fields";
    print '<table border="0" cellpadding="4" cellspacing="6">', "\n";
    print '<tr  bgcolor="#CCCCFF""><td colspan="2">', 
          "Select a job: </td></tr>";
    print "<tr>$tdtopright  </td>\n";

    print '<td><select name="joblist" >'; 

    foreach my $cj (@curr_jobs)
    {
        next unless $cj->use_online eq "y";
        my $id =  $cj->id;
        my $lab = sprintf("%-44s ID : %s",$cj->text,  $cj->id);
        my $jid = $q->param(-name=>"id");
        next if $id =~ /2012-02/;
        my $sel = ($lab =~ /$jid/ ) ? "selected" : "";
        print "<option $sel>", $lab, "</option>\n";
    }
    print "</select>\n";
    print "</td></tr>\n";

#curre    print "$req (for 2005-06)</td></tr>\n";

    my %cat_label = ( pers => "Personal Information:",
                      prof => "Professional Information:",
                      cont => "Contact Information:"
                    );
    foreach my $cat (  "pers", "cont",  "prof" )
    { 
       print '<tr  bgcolor="#CCCCFF""><td colspan="2">',"$cat_label{$cat} </td></tr>\n";
       foreach $t ( sort {$element_info{$cat}{$a}{rank} <=>
                       $element_info{$cat}{$b}{rank} } keys %{ $element_info{$cat}} )
       {  
          next if ( $element_info{$cat}{$t}{prompt} eq "Address");
          my $req_flag = $element_info{$cat}{$t}{required} ? $req : $sp;
          my $prompt =  $element_info{$cat}{$t}{prompt};  
     #     $prompt .= $req_flag if $element_info{$cat}{$t}{required};  
          print "<tr>$tdtopright  $prompt: </td>\n";
          my $value = $q->param(-name=>$t) ? $q->param(-name=>$t) : "";
#klugde for Phd default...
          $value = "PhD" if ( $t eq "LastDegree" and $value eq "" );
          my $out = input_query(\%{$element_info{$cat}{$t}}, $t, $value);
          print " "x4, $tdtop, "$out $req_flag</td>\n";
       
        }
     }
 
 #     print "<tr>$tdtopright Submit</td>",
       print '<tr><td align="left">', 
                 $q->button(-name=>'edit',-value=>'Submit',
                            -onclick=>"isStep2Complete(this.form)" ),
            '    </td></tr>',"\n";
      print "</table></center>\n";     
      print $q->hidden(-name=>'action',
                       -value=>'confirm');      
}

sub Hide_params 
{
 #    print "<h2> Hide_params:: call Job_Appl_Info3::get_elements </h2>";
     my @es = Job_Appl_Info3::get_elements();
     my $ja = new Job_Appl_Info3;
     my $jl = $q->param(-name=>"joblist");
#      print "Hide_params:: element joblist --> ", $jl, "<br />\n";
     my $id = $1 if ($q->param(-name=>"joblist") =~ /ID : .*?(\d\d\d\d-\d+)/);
#   print "Hide_params:: element id --> ", $id, "<br />\n";
#    dump_it();
#    return:
    Hide("id", $id);
    foreach my $e (@es)
    {  
      my $value = $q->param(-name=>$e) ? $q->param(-name=>$e): "";
  #    print "Hide_params:: element $e --> ", $value, "<br />\n";
      Hide($e, $value) if $q->param(-name=>$e);
    }
}

sub Hide
{
   my $name = shift;
   my $value = shift;

   print <<EndofHidden;
    <input type="hidden" name="$name"  value="$value">
EndofHidden

   return;
}

sub Save_params 
{
    my @es = Job_Appl_Info3::get_elements();
    my $ja = new Job_Appl_Info3;
    
    my $id = $q->param(-name=>"id");
 
    foreach my $e (@es)
    {  
        my $value = $q->param(-name=>$e) ? $q->param(-name=>$e): "";
        $value = "Not entered" if ($e eq "citizenship" and $value =~ /select/);
        $ja->$e($value);
    }
    my ($ynow,$monnow,$daynow) = Today();
    my $outdate = sprintf("%s-%2.2d-%2.2d", $ynow,$monnow,$daynow);
    my $remote_ip = $ENV{'REMOTE_ADDR'};
    $ja->Remote_IP($remote_ip);
    $ja->Date_Submitted($outdate);
    Job_Appl_Info3::saveit ($ja, $id);
    my $filename = $ja->File_Name;
    print $q->hidden(-name=>'id',       -value=>$id);
    print $q->hidden(-name=>'filename', -value=>$filename);
    my $email = $ja->email;
    my $lname = $ja->lname;

    send_email($email, $lname, $id);
    return;
}

sub send_email
{
    my $email = shift;
    my $name  = shift;
    my $id    = shift;
    my $subj  = "UBC Equity Survey";
    my $from  = 'jobs@phas.ubc.ca';
    my $mailer = "/usr/sbin/sendmail -oi -t ";
#    my $mfile = "/www/jobs/lib/equity_survey_email.txt";
    my $mfile = "/www/jobs/lib/equity_survey_email.$id.txt";
   
     print "<h2> send_email:: the email is {$email}</h2>";
    if (-f $mfile )
    {
        open (X,$mfile) || die "cannot open <$mfile> $!\n";
        local ( $/ );
        my $mess=<X>;
        $mess =~ s/XX_name_XX/$name/;
          print "<p>$mess</p>";
        open (MAIL, "|$mailer") || die "cannot mail pipe \n";

       print MAIL "To: $email\n";
       print MAIL "Subject:  $subj\n";
       print MAIL "From: $from \n";
       print MAIL "\n$mess\n.\n";

       close MAIL;
    }
    return;
}

sub input_query
{
   my $e_info = shift;
   my $t = shift;
   my $v = shift;
   my $out;
   if ($e_info->{qtype} eq "text")
   {
      
      $out .= '<input type="text" name="' 
           .  $t
           .  '" size="'
           .  $e_info->{nchar}  
           .  '"  maxlength="'
           .  $e_info->{maxchar}
           .  '" value="' . $v . '"'
           . ">\n";
 
   } elsif ($e_info->{qtype} eq "radio")
   {
      
      foreach my $ll (0..$#{$e_info->{label}})
      {
         $out .= "\n" . " "x12;
  
         my $val = $e_info->{value}[$ll];
         my $check = ($v eq $val) ? "checked" : "";
         $out .= '<input type="radio" name="'
              .  $t
              .  '" value="' 
              .   $val
              .   '" ' 
              .   $check . '>' . "$e_info->{label}[$ll]\n";
      }
   } elsif ($e_info->{qtype} eq "pulldown")
   {
      $out = '<select name="' . $t . '" size="1">' ."\n";
      foreach my $ll (0..$#{$e_info->{label}})
      {
         my $val = $e_info->{value}[$ll];
         my $l = $e_info->{label}[$ll];
         my $select = ($v eq $l) ? "selected" : "";
         $out .= '     <option name="' .$t.  '" '. " $select >" 
              .  "$l</option>\n";

      }
      $out .= "</select>\n";
   } 
   return $out;
}
sub footer
{
    print "<table><center>";
    print " <tr><td>",   $q->submit(-name=>'edit',-value=>'save'),                
           "</td><td>",  $q->submit(-name=>'edit',-value=>'back'), "</td></tr>\n";
    print "</table></center></form>\n";
    
    return  
}

sub welcome
{
     my $page_header = shift;

     my $pg_head =  $page_header ? $page_header : "";
     my $wel_text = $wel ? $wel : " ";

     print <<EndofWelcome2;
     <h2>$pg_head</h2>
     <p> $wel_text
     </p>
EndofWelcome2
   
    return;
}
sub Form_Welcome
{
     print welcome_text();
   
    return;
}

sub print_query
{
    my @es = Job_Appl_Info3::get_elements();
    my $e;
    my $f = $q->param(-name=>"filename");
    
    my $value;
    my $t = Job_Appl_Info3::rd_file($f);

    print "<h2>Print Query </h2>\n <table>";
      print "</table>\n";

  }
sub do_thanks
{
    my $Hidden = shift;
    my $ln = $q->param('lname');
    $wel = "<h2> Thank you Dr. $ln for the input... </h2>";
  
    welcome();
   
    print <<EndOffarewell;
    <p>
       A file has been opened for your application & your  information entered. <br />
       To this you can now, upload PDF files for your CV, Research Statement,
       Publication List and Teaching Interests.  If all this information
       is in a single file, please upload as a CV.   You can submit this documentation  at a 
       latter date via email to &lt;jobs\@phas.ubc.ca&gt; 
	Please quote the competition number in your email
       <br />
     
    </p>
EndOffarewell
#& Specialization 
     print " Do you wish to Upload PDF files ... ";
     print $q->submit(-name=>'goto_File',-value=>"UpLoad"), "\n";
     print '&nbsp;'x5;
     print $q->submit(-name=>'goto_File',-value=>"Not now"), "\n";
     Hide ("lname", $ln);
     return; 

}

sub dump_it
{
	print "<h2> Dump of the query </h2><br />\n";
        print $q->Dump;
        print "<hr />";
}
sub Get_Current_Jobs
{
   my @cjobs;
   my @jobs = Job_Ad_MetaData::rd_file();
   my ($y,$m,$d) = Today();
   my $grace = 64;				#number of grace days.
   
   my $now = $y * 10000
           + $m * 100
           + $d;

   foreach my $j (@jobs )  
   {
      next unless $j->use_online;    
      my $ex = $j->expires;
      my $y = int ($ex/10000);
      my $m = int ( ($ex -$y *10000)/100);
      my $d = $ex- $y*10000 - $m*100;
      my @ex_date = Date::Calc::Add_Delta_Days($y,$m,$d,$grace);
      my $true_exp = $ex_date[0]*10000 + $ex_date[1]*100 + $ex_date[2];
      next unless (   $now <=  $true_exp);  
  #    print " Get_Current_Jobs:: expires is ", $j->expires, "    ($y,$m,$d--> $true_exp) now is $now<br />";
      push @cjobs, $j;
 
   }
   
   return @cjobs;
}
sub welcome_text
{
   my $out = "<h1>$title $version </h1>";

   $out .= '<script src="/jobs/lib/jobs2.js"></script>'."\n";
  # $out .= '<link rel="stylesheet" href="/jobs/lib2/job.css">'. "\n"x5;
 

}
sub do_welcome_page
{
   my $email =  '<script>mk_phys_mail("jobs","Jobs")</script>';
   my $em_txt = ""; '&lt;jobs\@phas.ubc.ca&gt;';
   my $out = "";
   $out .= "<p> This is a form to  apply for a job";
   $out .= "    with the Physics and Astronomy Dept at UBC.   
                Note that submission of this 
                form does  <strong>NOT</strong> fully constitute a complete 
                application:  you must
                also submit a CV and 
                supporting documentation as detailed below,
                and arrange for 3 letters of recommendation to be submitted to
                $email $em_txt.   Please request that the authors quote the 
                competition number in the subject line.";
		
   $out .= '<p> Please see <a href="/physoffice/jobs/file_formats.phtml">File Formats</a> for acceptable formats.</p>';
   $out .= "<p>  Personal Information provided on this application is collected
                 pursuant to  section 26 of the Freedom of Information and 
                 Protection of Privacy Act,  RSBC, c. 165, and will be used 
                 to consider your application and will 
                 only be reviewed by those persons  within the University 
                 that are involved 
                 in the recruitment process. 

                Please read the Physics and Astronomy " . 
                '<a href="/physoffice/jobs/panda_privacy.html">' .
                " privacy statement</a> 
                regarding the use of the information requested. </p>";

     $out .=<<endOfexp;
<p>  The are a number of steps involved in this process...

<ol> <li> Identification & contact information is to be entered </li>
     <li> Confirmation of the entered data </li>
     <li> Either, 
           <ul><li> upload of a CV PDF and a PDF list  of publications, 
                   a research statement and 		            
                   a teaching statement 
                    with the form provided </li>

               <li> or send your CV and research/teaching statement by surface mail .</li>
           </ul>
    </li>
    <li>Arrange for 3 letters of reference to be sent to $email or to
        the address in the advertisment.</li>
<!--	
    <li>On receipt of all this required information (personal & contact info, 
        CV, & 3 reference letters) a notice of confirming email will be sent by us.
    </li>
    -->
</ul>
<p>Note that this form cannot be re-entered.  If you wish to upload documents via the
web form, please have your documents ready before starting.\&nbsp;</p>
endOfexp

   print $out;
   print $q->submit(-name=>'Apply',-value=>"Apply?"), "\n";

}          
sub do_FileUpload
{
    print "<h2>Upload PDF Documentation:</h2>\n";
    print "<p> Please enter  <strong>ALL</strong> the appropiate PDF file names before selecting Continue</p>
           
           <p> If you are not uploading one or more of Publications, Research, or Teaching because this
               information is already contained in your CV, please indicate such below: we will use these
               flags to help judge the completeness of your file.   
            </p><p> Use this to Upload PDF files only... If your want to submit doc files, please
               email them to &lt;jobs\@phas.ubc.ca&gt;
            (Hint: <em>We</em> use OpenOffice to convert doc files to PDF)
            </p>"; 
    my $this_fn = $q->param("filename");   
    my $jid       = $q->param("id");
    my $this_appl = (split "/", $this_fn)[-2];
  
    my $or = "<td> <strong><em> OR </em> </strong></td>";
    print "<table>";
    foreach my $fn ( sort keys %Upload_File_Prompts)
    {
        print "<tr><td>$Upload_File_Prompts{$fn} : </td><td>", 
               $q->filefield(-name=>$fn,
	                     -default=>' ',
	                     -size=>50,
	 		     -maxlength=>80),
           "</td>";
        print "$or<td>My Publications are in the CV PDF ", $q->checkbox(-name=>"Pubs_In_CV",
                                                                -label=>''),                
              " </td> \n"  if $fn eq "Pubs";
        print "$or<td>My Research Statement is in the CV PDF ", $q->checkbox(-name=>"Research_In_CV",
                                                                -label=>''),                
              " </td> \n"  if $fn eq "Research";
         print "$or<td>My Teaching Statement is in the CV PDF ", $q->checkbox(-name=>"Teach_In_CV",
                                                                -label=>''),                
              " </td> \n"  if $fn eq "Teach";
        print "</tr>\n";
    }
    print "</table>";
    print $q->submit(-name=>'Read_File',-value=>"Continue?"), "\n";
    my $filename = $q->param('filename');
    print $q->hidden(-name=>'filename', -value=>$filename);

    print $q->hidden('Job_ID', $jid), "\n";
    print $q->hidden('This_Appl',$this_appl ),"\n"; 
    print $q->hidden('lname',  $q->param('lname') );
}
sub do_Read_File
{
     use Digest::MD5;
#    print "<h2>do_Read_File</h2>\n";
    my $this_appl = $q->param("This_Appl");   
    my $jid       = $q->param("Job_ID");
    my %Have = ();
    my $results = "";
    my $res_cv = "";
#    print " input is job $jid, appl $this_appl <br />";
    Job_Appl_Info3::Set_xml_dir($jid);
    my $ja = Job_Appl_Info3::rd_file($this_appl);
    my $jtit = Job_Ad_MetaData::Job_Title($jid);
    print "<h2> Results of file uploading for Dr. ",$q->param('lname'), " in <br />$jid: $jtit:</h2>"; 

    my $xp;
    foreach my $tag ( keys %Upload_File_Prompts)
    {
       $Have{$tag} = "NOT uploaded.";
    }
    print "<table>";
     foreach my $tag ( qw [ Pubs Teach Research ] )
     {
         my $qp = $tag. "_In_CV";
         if ($q->param($qp) )
         {
       #     print "setting Pubs file to In_CV_File";
            my $outfile ="In_CV_File";
            $ja->$tag($outfile);
            $Have{$tag} = "is contained within the CV\n";
         
         }
     }
    foreach my $tag ( keys %Upload_File_Prompts)
    {
       my $filename = $q->param($tag);
       next unless $filename;
       my $of = ($tag eq "other_file") ? "Other_".$filename : $tag;
       my $outfile = Job_Appl_Info3::abs_file_path($jid, $this_appl, $of);
     #  print "outfile is $outfile<br /> \n";
    # Copy a binary file to somewhere safe
       open (OUTFILE,">$outfile");
       my $total= 0;
       my $is_pdf = 0;
    #   print "The results of the file uploading are:  <br />" unless $xp;
       $xp++;
       while (<$filename>)
       {
          $is_pdf++ if (/%PDF/);
          print OUTFILE;
       }
       close OUTFILE;
 
 
       if ( $is_pdf)
       {
          open (OUTFILE,"$outfile");
          binmode(OUTFILE);
          my $md5 =  Digest::MD5->new->addfile(*OUTFILE)->hexdigest;
          close OUTFILE;
          my $size = -s $outfile;
          $of =~ s/^Other_//;
          $Have{$tag} = "has  $size bytes <br />
                         The md5sum is $md5";
          $ja->$tag($outfile);
          
        } else
        {
           $Have{$tag} = "does not look like a PDF format and will not be saved";
           unlink $outfile;
        }
 
     }
     foreach my $tag ( ( sort keys %Upload_File_Prompts) )
     { 
        print '<tr><td valign="top">', " File <strong>$tag</strong> </td>\n";
        print "    <td>$Have{$tag}</td></tr>\n";
     }
     print "</table>\n";

 #    print "Call savit to store results <br />";
     Job_Appl_Info3::saveit($ja, $jid) if $xp;

    print $q->submit(-name=>'Done',-value=>"Done"), "\n";  
    my $filename = $q->param('filename');
    print $q->hidden(-name=>'filename', -value=>$filename);

    print $q->hidden('Job_ID', $jid), "\n";
    print $q->hidden('This_Appl',$this_appl ),"\n";
    print $q->hidden('lname', $q->param('lanme') ),"\n";
}

sub do_No_CV
{
    my $id = $q->param(-name=>"id");
 
    print <<Endofbye;
<p> You have chosen not to submit a CV at this time...
</p>
<p> Please submit your CV either by email to Jobs\@physics.ubc.ca 
    with <strong>$id</strong> in the Subject Line,  
<br />.
</p>
     <h3>Goodbye &amp; Bon Chance ! </h3>
Endofbye

    return;
}
sub do_Done
{
    my $Hidden = shift;
    my $ln = $q->param('lname');
    $wel = "<h2> Thank you Dr. $ln for the input... </h2>";
  
    welcome();
   
    print <<EndOffarewell;
    <p>
       Your information has been stored. <br />
       We wish you success.  The committee should contact you after the review process.

       <br />
    
    </p>
EndOffarewell
 
     return; 

}
