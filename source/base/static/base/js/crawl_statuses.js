var statuses = statuses || {};

(function(){

  /**
  * Crawl Dashboard interactions
  */
  statuses.buttons = {
    play: "playButton",
    stop: "stopButton",
    restart: "restartButton",
    images: "dumpImages",
    cca: "common-crawl-dump",
    rounds: "rounds",
    log: "getCrawlLog",
    seeds: "getInitialSeeds",
  }

  /**
  * This object contains information on which buttons should be enabled or
  * disabled based on the status of the crawl.
  */
  statuses.states = {
    "NOT STARTED": {
      "disabled": [
        "stop",
        "restart",
        "images",
        "cca",
        "log",
      ],
      "enabled": [
        "play",
        "rounds",
        "seeds",
      ],
    },
    "STARTING": {
      "disabled": [
        "stop",
        "restart",
        "images",
        "cca",
        "play",
        "rounds",
      ],
      "enabled": [
        "log",
        "seeds",
      ],
    },
    "STARTED": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "INJECT": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "GENERATE": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "FETCH": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "PARSE": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "UPDATEDB": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "INVERTLINKS": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "INDEX": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "DEDUP": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
      ],
      "enabled": [
        "stop",
        "log",
        "seeds",
      ],
    },
    "RESTARTING": {
      "disabled": [
        "play",
        "restart",
        "images",
        "cca",
        "rounds",
        "stop",
        "log",
        "seeds",
      ],
      "enabled": [
      ],
    },
    "SUCCESS": {
      "disabled": [
        "play",
        "stop",
      ],
      "enabled": [
        "restart",
        "images",
        "cca",
        "rounds",
        "log",
        "seeds",
      ],
    },
    "FAILURE": {
      "disabled": [
        "stop",
        "restart",
        "images",
        "cca",
        "play",
        "rounds",
      ],
      "enabled": [
        "log",
        "seeds",
      ],
    },
    "STOPPING": {
      "disabled": [
        "stop",
        "restart",
        "images",
        "cca",
        "play",
        "rounds",
      ],
      "enabled": [
        "log",
        "seeds",
      ],
    },
    "STOPPED": {
      "disabled": [
        "stop",
        "images",
        "cca",
        "play",
        "rounds",
      ],
      "enabled": [
        "restart",
        "log",
        "seeds",
      ],
    },
    "FINISHING": {
      "disabled": [
        "stop",
        "restart",
        "images",
        "cca",
        "play",
        "rounds",
      ],
      "enabled": [
        "log",
        "seeds",
      ],
    },
    "FORCE STOPPED": {
      "disabled": [
        "stop",
        "restart",
        "images",
        "cca",
        "play",
        "rounds",
      ],
      "enabled": [
        "log",
        "seeds",
      ],
    },
    "REDIS ERROR": {
      "disabled": [
        "stop",
        "images",
        "cca",
        "play",
        "log",
        "seeds",
      ],
      "enabled": [
        "restart",
        "rounds",
      ],
    },
    "CELERY ERROR": {
      "disabled": [
        "stop",
        "images",
        "cca",
        "play",
        "log",
        "seeds",
      ],
      "enabled": [
        "restart",
        "rounds",
      ],
    },
  }
})();
