#!/bin/sh
mail -s "$(echo -e "$1 $DATE_INFO\nContent-Type: text/html;charset=utf-8")" $2 < MailBody
