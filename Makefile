########################|	leaver/mrms-ldm:latest		|########################
build:
	docker build \
	-t leaver/mrms-ldm:latest \
	-f Dockerfile \
	.

########################|				|########################
run:
	docker run -d \
	-p 80:80 \
	leaver/mrms-ldm:latest

########################|				|########################
prune:
	docker container prune -f && \
	docker image prune -f

########################|				|########################
remove:
	docker image rm leaver/mrms-ldm:latest
