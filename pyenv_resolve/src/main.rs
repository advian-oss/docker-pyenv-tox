use semver::Version;
use shellfn::shell;
use std::env;
use std::error::Error;

#[shell]
fn pyenv_list_installed() -> Result<impl Iterator<Item = String>, Box<dyn Error>> {
    r#"
    pyenv versions
"#
}

#[shell]
fn pyenv_list_available() -> Result<impl Iterator<Item = String>, Box<dyn Error>> {
    r#"
    pyenv install -l
"#
}

fn pyenv_parse_semver(input: String) -> Result<Version, semver::Error> {
    let trimmed = input.trim().trim_start_matches("* ");
    let parts: Vec<&str> = trimmed.split(" ").collect();
    Version::parse(parts[0])
}

fn main() {
    // Figure out what versions to look for
    let args: Vec<String> = env::args().collect();
    let mut unresolved_requested_versions: Vec<String> = Vec::with_capacity(args.len() - 1);
    let mut resolved_versions: Vec<Version> = Vec::with_capacity(args.len() - 1);
    let mut look_for: Vec<Version> = Vec::with_capacity(args.len() - 1);
    for item in args {
        if item.ends_with("pyenv_resolve") {
            continue;
        };
        match Version::parse(&item) {
            Err(_) => {
                let vminor = item.clone() + ".1337715517-parsermarker";
                match Version::parse(&vminor) {
                    Ok(ver2) => look_for.push(ver2),
                    Err(_) => unresolved_requested_versions.push(item.clone()),
                }
            }
            // If the version was already fully defined just put it in the final vector
            Ok(ver) => resolved_versions.push(ver),
        };
    }
    look_for.sort();
    let look_for = look_for;
    let unresolved_requested_versions = unresolved_requested_versions;
    // println!("look_for: {:?}", look_for);
    // println!("unresolved_requested_versions: {:?}", unresolved_requested_versions);

    // Figure out which versions are installed
    let pyenv_inst = pyenv_list_installed().unwrap();
    let mut installed_versions: Vec<Version> = Vec::with_capacity(5);
    for verstr in pyenv_inst {
        match pyenv_parse_semver(verstr) {
            Ok(ver) => installed_versions.push(ver),
            Err(_) => {}
        }
    }
    installed_versions.sort();
    let installed_versions = installed_versions;
    // println!("installed_versions: {:?}", installed_versions);

    // Figure out which versions are available
    let pyenv_avail = pyenv_list_available().unwrap();
    let mut available_versions: Vec<Version> = Vec::with_capacity(50);
    for verstr in pyenv_avail {
        match pyenv_parse_semver(verstr) {
            Ok(ver) => available_versions.push(ver),
            Err(_) => {}
        }
    }
    available_versions.sort();
    let available_versions = available_versions;
    // println!("available_versions: {:?}", available_versions);

    for wanted_ver in look_for {
        let mut selected_ver: Version = wanted_ver.clone();
        for check_ver_inst in &installed_versions {
            if check_ver_inst.major != wanted_ver.major {
                continue;
            };
            if check_ver_inst.minor != wanted_ver.minor {
                continue;
            };
            selected_ver = check_ver_inst.clone();
        }
        // If we got a version from the installed go to next wanted
        if selected_ver.patch != wanted_ver.patch && selected_ver.pre != wanted_ver.pre {
            resolved_versions.push(selected_ver);
            continue;
        }
        for check_ver_avail in &available_versions {
            if check_ver_avail.major != wanted_ver.major {
                continue;
            };
            if check_ver_avail.minor != wanted_ver.minor {
                continue;
            };
            selected_ver = check_ver_avail.clone();
        }
        if selected_ver.patch == wanted_ver.patch && selected_ver.pre == wanted_ver.pre {
            panic!("Selected version equals wanted version, this should not happen!");
        }
        resolved_versions.push(selected_ver);
    }
    let resolved_versions = resolved_versions;
    //println!("resolved_versions: {:?}", resolved_versions);
    for ver in resolved_versions {
        print!("{} ", ver.to_string())
    }
    for ver in unresolved_requested_versions {
        print!("{} ", ver)
    }
    println!("");
}
