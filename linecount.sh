find . | grep -E "(\.py$)|(\.sh$)" | sed -e 's/ /\\ /g' | xargs wc -l
