#!/usr/local/bin/perl
$ver = '1.1';    # 変更しないで下さい
#+--------------------------------------------------------------------
#|DLViewer (カウント数一覧を表示)                           2016/08/25
#|(C)2000 不可思議絵の具(http://ygkb.jp/)
#+--------------------------------------------------------------------
#|●更新履歴
#|  1.1 2016/08/25  出力結果をHTML5化
#|  1.0 2000/07/28  サクサクっと流用パーツで作成。
#+--------------------------------------------------------------------
#|●使い方
#|  1. 下の２つの設定項目を埋めます。
#|  2. dlv.cgi を dl.cgi と同じフォルダにASCIIモードでアップロード。
#|  3. dlv.cgi のパーミッションを 705 又は 755 にします。
#|  4. http://DLをインストールしたURL/dlv.cgi を呼び出します。　以上。
#+--------------------------------------------------------------------
# [ログファイルを格納したディレクトリの名前]
# ログ用ディレクトリは dl/ 以下に作って下さい。
$Dir_Log = 'log';

# [時差の修正]
# 海外にサーバがある場合、「日本からの時差(ここが紛らわしいので注意)」
# を指定して下さい。　(サーバが日本にある場合はそのままで)
# 例えば、アメリカ(ニューヨーク)の場合は -14 とします。
# ※要は表示させたときに日本時刻に合うように調整すればいいです(^^;
$TZ_ADJ = +0;

#+--------------------------------------------------------------------
# (設定ここまで)
#+--------------------------------------------------------------------
# ※ここからは分かる人だけ弄って下さい。
# 　(タブのサイズ・[4]、折返し・[無し]で綺麗に表示されます)
#+--------------------------------------------------------------------
#|&main
#+--------------------------------------------------------------------
### ディレクトリを修正
$Dir_Log = "./$Dir_Log/";

### 時差の修正
$TZ_ADJ = $TZ_ADJ*3600;

### ファイル一覧を取得
opendir(DIR, "$Dir_Log");
unless (-e $Dir_Log) { closedir(DIR); &Func_PutError("指定されたディレクトリ ($Dir_Log) が見つかりません。"); exit(1); }
unless (-r $Dir_Log) { closedir(DIR); &Func_PutError("指定されたディレクトリ ($Dir_Log) を開くことが出来ませんでした。<BR>パーミッションが 705又は755 になっているか確認して下さい。"); exit(1); }
@FILENAME = readdir(DIR);
closedir(DIR);
@FILENAME = sort({$a cmp $b} @FILENAME);


### ファイルリスト一覧から不適合ファイルを取り去る
### 対象 : ディレクトリ([.] [..]) / 拡張子が.logでない物
for ($i=0 ; $i < $#FILENAME+1 ; $i++) {
	if (($FILENAME[$i] eq '.') || ($FILENAME[$i] eq '..') || ($FILENAME[$i] =~ /.[^lL][^oO][^gG]$/)) {
		splice(@FILENAME,$i,1); $i--;
	} else {
		$FILENAME[$i] =~ s/.log$//i;							# 拡張子を取り去る
	}
}


foreach $filename (@FILENAME) {
	unless (open(LOG,"<${Dir_Log}${filename}.log")) { next; }	# 適合したファイルのみを開く
	flock(LOG,1);
	chop($count = <LOG>);

	$updtime = (stat(LOG))[9];									# ファイル更新時刻(現地時間)を取得
	$updtime = $updtime - $TZ_ADJ;								# 時差の修正

	push(@LOG, sprintf("%06d#%s#%s", $count, $filename, $updtime));

	flock(LOG,8);
	close(LOG);
}


@LOG = sort({$b cmp $a} @LOG);


### 結果表示
&HTML_Head;
print "<table>\n";

#print "<thead>\n";
print "<tr class='tableHeader'>";
print "<th>対象ファイル</th>";
print "<th>カウント数</th>";
print "<th>最終カウント日時</th>";
print "</tr>\n";
#print "</thead>\n";

#print "<tbody>\n";
$sum = 0;
foreach $line (@LOG) {
	($count, $logname, $updtime) = split(/#/, $line);
	$count = int($count);
	$updtime = &Func_MakeDate($updtime);
	$sum += $count;
	print "<tr>";
	print "<th class='filename'>$logname</th>";
	print "<td class='count'>$count</td>";
	print "<td class='updTime'>$updtime</td>";
	print "</tr>\n";
}
#print "</tbody>\n";

#print "<tfoot>\n";
print "<tr class='tableFooter'>";
print "<th class='filename'>計</th>";
print "<td class='count'>$sum</td>";
print "<td>&nbsp;</td>";
print "</tr>\n";
#print "</tfoot>\n";

print "</table>\n";

&HTML_Tail;

exit(0);


#+--------------------------------------------------------------------
#|サブルーチン
#+--------------------------------------------------------------------
### [エラー出力]
sub Func_PutError {
	local($mesg) = @_;
	&HTML_Head;
	print "<center><p><b>[Error]</b>$mesg</p></center>\n";
	&HTML_Tail;
	exit(1);
}


### 通算秒から日時を得る関数
### (通算秒(1970/01/01 00:00:00から)を放り込むと[年/月/日/(曜) 時:分:秒]の文字列に整形して返す)
sub Func_MakeDate {
	local($t) = @_;
	local(@wdays,$sec,$min,$hour,$day,$mon,$year,$wday);
	@wdays = ("日","月","火","水","木","金","土");
	($sec,$min,$hour,$day,$mon,$year,$wday) = localtime($t);
	return sprintf("%d/%02d/%02d(%s) %02d:%02d:%02d",1900+$year,$mon+1,$day,$wdays[$wday],$hour,$min,$sec);
}


### HTML 頭の部分
sub HTML_Head {
print <<"END";
Content-type: text/html

<!DOCTYPE html>
<html>
<head>
	<meta name="robots" content="noindex,nofollow">
	<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">
	<meta http-equiv=\"Content-Style-Type\" content=\"text/css\">
	<title>DLViewer</title>
	<style type=\"text/css\"><!--
		body {
			font-family:Arial,Verdana;
			background-color: #ffffff;
			color: #7e2828;
		}

		a {
			text-decoration: none;
			font-weight: bold
		}
		a:link {
			color: #7726c8;
		}
		a:active {
			color: #5c4fff;
		}
		a:hover {
			text-decoration: underline;
		}
		a:visited {
			color: #ff5959;
		}

		table {
			border-collapse: collapse;
			border: 1px #7e2828 solid;
			margin-left: auto;
			margin-right: auto;
		}
		th, td {
			border: 1px #7e2828 solid;
			padding-left: 1em;
			padding-right: 1em;
			padding-top: 3px;
			padding-bottom: 3px;
		}

		.tableHeader {
			background-color: #ffeeee;
		}
		.tableFooter {
			background-color: #ffeeee;
		}
		.filename {
			text-align: left;
		}
		.count {
			text-align: right;
		}
		.updTime {
			text-align: left;
		}

		.copyright {
			text-align: right;
		}
	--></style>
</head>

<body>

<h1>DLViewer $ver</h1>
<hr>

END
}


### HTML しっぽの部分
sub HTML_Tail {
	print "<hr>\n";
	print "<div class='copyright'><a href=\"http://ygkb.jp/\">[DLViewer $ver] / &copy;2000 Enogu Fukashigi\@YugenKoubou</A></div>\n";
	print "</body>\n</html>\n";
}
