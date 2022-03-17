use shellfn::shell;
use std::error::Error;
use std::env;
use semver::{BuildMetadata, Prerelease, Version};

#[shell]
fn pyenv_list_installed() -> Result<impl Iterator<Item=String>, Box<dyn Error>> { r#"
    pyenv versions
"# }

#[shell]
fn pyenv_list_available() -> Result<impl Iterator<Item=String>, Box<dyn Error>> { r#"
    pyenv install -l
"# }

fn pyenv_parse_semver(input: String) -> Result<Version, semver::Error> {
    let trimmed = input.trim().trim_start_matches("* ");
    let parts: Vec<&str> = trimmed.split(" ").collect();
    Version::parse(parts[0])
}

fn main() {
    println!("Hello, world!");

    // Figure out what versions to look for
    let mut args: Vec<String> = env::args().collect();
    let mut look_for: Vec<Version> = Vec::with_capacity(args.len()-1);
    for item in args {
        if item.ends_with("pyenv_resolve") { continue };
        match Version::parse(&item)   {
            Err(_) => {
                let vminor = item + ".1337715517-parsermarker";
                match Version::parse(&vminor) {
                    Ok(ver2) => look_for.push(ver2),
                    Err(_) => continue,
                }
            },
            Ok(ver) => look_for.push(ver),
        };
    }
    println!("look_for: {:?}", look_for);

    // Figure out which versions are installed
    let pyenv_inst = pyenv_list_installed().unwrap();
    let mut installed_versions: Vec<Version> = Vec::with_capacity(5);
    for verstr in pyenv_inst {
        match pyenv_parse_semver(verstr) {
            Ok(ver) => installed_versions.push(ver),
            Err(_) => {}
        }
    }
    println!("installed_versions: {:?}", installed_versions);


    // Figure out which versions are available
    let pyenv_avail = pyenv_list_available().unwrap();
    let mut available_versions: Vec<Version> = Vec::with_capacity(50);
    for verstr in pyenv_avail {
        match pyenv_parse_semver(verstr) {
            Ok(ver) => available_versions.push(ver),
            Err(_) => {}
        }
    }
    println!("available_versions: {:?}", available_versions);

}
