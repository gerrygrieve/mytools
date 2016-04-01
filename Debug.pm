package Debug;

my $Debug = 0;
my $Color = "red";
my $def_fmt = "html";
1;


sub Set_Debug
{
    my $in = shift;
    my $fmt = shift;
    $Debug = $in;
    $format = $fmt ? $fmt :  $def_fmt; 
 
    return $in;

}

sub Set_Debug_Color
{
    my $in = shift;
    my $old =  $Color;
    $Color = $in;
    return $old;    
}

sub dsay 
{
#       print qq{<h2 style="color: red;"> Debug::dsay {$Debug}</h2>\n};
    return unless $Debug;
    my $mesg = shift;


    if ($format eq "html")
    {
       print qq{<h2 style="color: $Color;"> $mesg  </h2>\n};
    } else
    {
      print "DEBUG-> $mesg \n";
    }

    return;
}


