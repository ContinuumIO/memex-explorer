#!/usr/bin/env bash

mkdir -p app/resources/seeds
mkdir -p app/resources/models
mkdir -p app/resources/crawls
mkdir -p app/resources/image_space/uploaded_images

chmod -R a+rwX app/resources/seeds
chmod -R a+rwX app/resources/models
chmod -R a+rwX app/resources/crawls
chmod -R a+rwX app/resources/image_space