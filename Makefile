password=""
username=""
server=""

protobuff:
	protoc -I=streetlearn --python_out=streetlearn/buff $streetlearn/proto/addressbook.proto
download-original:
	rsync -p -r -e 'ssh -p41000' geyang@localhost:/private/home/geyang/fair/streetlearn/pittsburgh_512.tar.gz /Users/geyang/fair/streetlearn/data
upload-processed:
	rsync -P -r --exclude="manhattan" --exclude="pittsburgh" --relative processed-data -e 'ssh -p41000' geyang@localhost:/private/home/geyang/fair/streetlearn
vector-upload-processed:
	sshpass -p ${password} rsync -P -r --exclude="manhattan" --exclude="pittsburgh" --relative processed-data -e 'ssh' ${username}@${server}:/h/${username}/fair/streetlearn --info=progress2
collect-summary:
	find . -name "summary.md" | xargs cat >> Makefile
